from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import Group, User, PermissionsMixin, AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.loader import *
from django.utils.translation import gettext_lazy as _
from django_signal_notifier.message_templates import message_template_names, get_message_template_from_string
from django_signal_notifier.messengers import get_messenger_from_string, messenger_names
from . import settings as app_settings


class DSN_Profile(models.Model):
    user = models.OneToOneField(to=app_settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    telegram_chat_id = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        if self.user is None:
            return 'profile _'
        else:
            return "%s: %s %s" % (self.user.username, self.user.first_name, self.user.last_name)


class Backend(models.Model):
    """
    Backend used to send messages
    """
    messenger = models.CharField(  # use it instead of  ModelSignal tentatively
        max_length=128,
        default="BaseMessanger",
        choices=messenger_names,
    )

    message_template = models.CharField(
        max_length=128,
        default="BaseMessageTemplate",
        choices=message_template_names,
    )

    def send_message(self, users, trigger_context, **signal_kwargs):
        messengerClass = get_messenger_from_string(self.messenger)
        if messengerClass is not None:
            templateMessageClass = get_message_template_from_string(self.message_template)
            if templateMessageClass is not None:
                templateMessage = templateMessageClass()
                msngr = messengerClass()
                msngr.send(template=templateMessage, users=users, trigger_context=trigger_context,
                           signal_kwargs=signal_kwargs)
            else:
                print("Can't any message_template with this name")
                raise ValueError("Can't any message_template with this name")
        else:
            print("Can't any messenger with this name")
            raise ValueError("Can't any messenger with this name")

    def __str__(self):
        return '[Messenger: {}] , [Message_template: {}]'.format(
            self.messenger,
            self.message_template
        )


class Trigger(models.Model):
    """	contains signal from specific sender. Actually is a activity accrued by the signal"""

    verb_signal_list = {}  # Used to map signal name(verb_name) to signal(verb_signal),
    # Must be set in apps.py by set_verb_signal_list or add_verb_signal

    # Activity Verb:
    verb = models.CharField(  # use it instead of  ModelSignal tentatively
        max_length=128,
        db_index=True,
    )

    # Activity Action_Object:
    action_object_content_type = models.ForeignKey(ContentType, blank=True, null=True, related_name='action_object',
                                                   on_delete=models.CASCADE, db_index=True)
    action_object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    action_object = GenericForeignKey("action_object_content_type", "action_object_id")

    # Activity Actor_Object:
    actor_object_content_type = models.ForeignKey(ContentType, blank=True, null=True, related_name='actor_object',
                                                  on_delete=models.CASCADE, db_index=True)
    actor_object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    actor_object = GenericForeignKey('actor_object_content_type', 'actor_object_id')

    # Activity Target:  # use it instead of  ModelSignal tentatively
    target = models.CharField(max_length=128, blank=True, null=True, db_index=True)

    def __str__(self):
        return '[Verb: {}] , [Action object: {}] , [Actor object: {}] , [Target: {}]'.format(
            self.verb,
            "{}:{}".format(self.action_object_content_type,
                           "instance(pk = {})".format(self.action_object_id)
                           if self.action_object_id is not None and self.action_object_id != "" else "Model itself")
            if (self.action_object_content_type is not None and self.action_object_content_type != "") else _(
                "Something"),
            "{}:{}".format(self.actor_object_content_type,
                           "Instance of model(pk = {})".format(self.actor_object_id)
                           if self.actor_object_id is not None and self.actor_object_id != "" else "Model itself")
            if (self.actor_object_content_type is not None and self.actor_object_content_type != "") else _("All"),
            self.target if (self.target is not None and self.target != "") else _("Everywhere")
        )

    def handler(self, **signal_kwargs):
        if self.match_signal_trigger(**signal_kwargs):
            all_subscriptions = self.subscriptions.filter(enabled=True)
            trigger_context = dict(action_object=self.action_object,
                                   action_object_content_type=self.action_object_content_type,
                                   actor_object=self.actor_object,
                                   actor_object_content_type=self.actor_object_content_type,
                                   verb=self.verb,
                                   target=self.target,
                                   )

            for subscription in all_subscriptions:
                for backend in subscription.backends.all():
                    backend.send_message(subscription.subscribers.all(), trigger_context, **signal_kwargs)

    def match_signal_trigger(self, **signal_kwargs):
        """
        Check trigger parameters and the signal then calls it if their match their selves
        self.verb and self.action_object_content_type(sender)(if is provided) checked by trigger
        Trigger parameters are :
        self.action_object_object_id
        self.actor_object_id
        self.actor_content_type
        self.target
        :return: Boolean
        """

        action_object = signal_kwargs.pop('action_object',
                                          signal_kwargs.pop('instance', signal_kwargs.pop('sender', None)))
        # sender is action_object class, but you can use action_object to access specific instance

        actor_object = signal_kwargs.pop('actor_object', None)
        target = signal_kwargs.pop('target', None)

        # action_object_id = None
        # if type(action_object.pk) != property:  # It's not a model, It's an object(model instance)
        #     action_object_id = action_object.pk

        if action_object is not None:
            action_object_class = action_object
            action_object_id = None
            if type(action_object.pk) != property:  # It's not a model, It's an object(model instance)
                action_object_class = action_object.__class__
                action_object_id = action_object.pk
            action_object_content_type = ContentType.objects.get_for_model(action_object_class)
        else:
            action_object_content_type = None
            action_object_id = None

        if actor_object is not None:
            actor_object_class = actor_object
            actor_object_id = None
            if type(actor_object.pk) != property:  # It's not a model, It's an object(model instance)
                actor_object_class = actor_object.__class__
                actor_object_id = actor_object.pk
            actor_object_content_type = ContentType.objects.get_for_model(actor_object_class)
        else:
            actor_object_content_type = None
            actor_object_id = None

        # We know that self.verb and self.action_object_content_type equal to signal name and sender class accordingly,
        # So we just check the other paramters of trigger :
        #   action_object_object_id ,
        #   actor(actor_object_content_type and actor_object_id):
        #   trigger
        if (self.action_object_content_type == None or (action_object_content_type == self.action_object_content_type)) and \
                (self.action_object_content_type == None or (actor_object_content_type == self.actor_object_content_type)) and \
                (self.target is None or self.target == "" or (target == self.target)):

            # If action_object_id is None, it means action_object is a class not an object, So does actor.
            if (self.action_object_id == None or (self.action_object_id == action_object_id)) and \
                    (self.actor_object_id == None or (self.action_object_id == actor_object_id)):
                return True

        return False

    # Each custom signal(non pre-defined signal like pre_save) must be introduced to DSN in each running
    # It must be done in ready function in apps.py before calling reconnect_all_triggers
    @classmethod
    def init_custom_signal(cls, signal_name, signal):
        cls.init_verb_signal(signal_name, signal)

    @classmethod
    def disconnect_all_triggers(cls):
        pass

    @classmethod
    def create_all_triggers(cls, signal):
        # ???????
        triggers = cls.objects.get_or_create(
            key=signal.__name__,
        )

    @classmethod
    def register_trigger(cls, verb_name, action_object=None, actor_object=None, target=None):
        """
        Create a Trigger for an Activity and connect the verb_signal to the Trigger.handler

        :param verb_name: string, activity verb, It usually is the name of the signal
        :param target: string, activity target
        :param action_object: object or model, activity action_object
        :param actor_object: object or model, activity actor_object
        :return: None
        """

        # verb_signal: ModelSignal, a signal that we want connect it the Trigger.handler method
        if verb_name in cls.verb_signal_list:
            verb_signal = cls.verb_signal_list[verb_name]  # Get signal function from verb_signal_list
        else:
            raise ValueError(
                "Invalid verb_name verb: First the verb name must be add to Trigger.verb_signal_list(use " + \
                "add_verb_signal() " + \
                " or set_verb_signal_list())")

        # action_object_class = action_object
        # action_object_id = None
        # if type(action_object.pk) != property:  # It's not a model, It's an object(model instance)
        #     action_object_class = action_object.__class__
        #     action_object_id = action_object.pk
        #
        # action_object_content_type = ContentType.objects.get_for_model(action_object_class)

        if action_object is not None:
            action_object_class = action_object
            action_object_id = None
            if type(action_object.pk) != property:  # It's not a model, It's an object(model instance)
                action_object_class = action_object.__class__
                action_object_id = action_object.pk
            action_object_content_type = ContentType.objects.get_for_model(action_object_class)
        else:
            action_object_content_type = None
            action_object_id = None

        if actor_object is not None:
            actor_object_class = actor_object
            actor_object_id = None
            if type(actor_object.pk) != property:  # It's not a model, It's an object(model instance)
                actor_object_class = actor_object.__class__
                actor_object_id = actor_object.pk
            actor_object_content_type = ContentType.objects.get_for_model(actor_object_class)
        else:
            actor_object_content_type = None
            actor_object_id = None

        # Trigger Creation
        # at first time, it should be created and just be get for next time
        # So make sure that get_or_create works properly
        try:
            trigger = cls.objects.get_or_create(
                verb=verb_name,
                action_object_content_type=action_object_content_type,
                action_object_id=action_object_id,
                actor_object_content_type=actor_object_content_type,
                actor_object_id=actor_object_id,
                target=target, )[0]
            if action_object_content_type:
                verb_signal.connect(trigger.handler, sender=action_object_class, dispatch_uid=str(trigger), weak=False)
            else:
                verb_signal.connect(trigger.handler, sender=None, dispatch_uid=str(trigger), weak=False)
            return trigger
        except Exception as e:  # Todo: It's not true to catch all of exception
            # raise IntegrityError("Subscription already made\nError message: {}".format(e))
            print("Exception: ", e)

    # connect verb_signal to Trigger.handler

    @classmethod
    def init_verb_signal(cls, verb_name, verb_signal):
        if verb_name in cls.verb_signal_list:
            raise ValueError("A signal with same name has already existed.")
        else:
            cls.verb_signal_list[verb_name] = verb_signal
        for trigger in cls.objects.filter(verb=verb_name):
            if trigger.action_object_content_type is not None:
                verb_signal.connect(trigger.handler, sender=trigger.action_object_content_type.model_class(),
                               dispatch_uid=str(trigger), weak=False)
            else:
                verb_signal.connect(trigger.handler, sender=None,
                               dispatch_uid=str(trigger), weak=False)

    @classmethod
    def set_verb_signal_list(cls, verb_signal_list):
        cls.verb_signal_list = verb_signal_list

    @classmethod
    # Todo: write a test for this function(It's not usual because we should rerun the app completely to check its functionality)
    def reconnect_all_triggers(cls):
        for trigger in cls.objects.all():
            signal = cls.verb_signal_list[trigger.verb]
            if trigger.action_object_content_type is not None:
                signal.connect(trigger.handler, sender=trigger.action_object_content_type.model_class(),
                               dispatch_uid=str(trigger), weak=False)
            else:
                signal.connect(trigger.handler, sender=None,
                               dispatch_uid=str(trigger), weak=False)


# Todo: implement it
# @classmethod
# def get_by_key(cls, key, content_type=None):
#     if key in _notification_type_cache:
#         return _notification_type_cache[key]
#     try:
#         nt = cls.objects.get(key=key)
#     except cls.DoesNotExist:
#         nt = cls.objects.create(key=key, content_type=content_type)
#     _notification_type_cache[key] = nt
#     return nt


class Subscription(models.Model):
    backends = models.ManyToManyField(
        Backend,
        blank=True,
        verbose_name=_('Backend'),
        help_text=_('Backend that specified for this subscription.\n '
                    'Important: Make sure that this backend message_template content can be adaptable to the trigger context'),
        # related_name='nyt_subscription',
    )

    receiver_groups = models.ManyToManyField(
        Group,
        blank=True,
        verbose_name=_('Receiver_Groups'),
        help_text=_('Groups that are related to this subscription.'),
        # related_name='nyt_subscription',
    )

    receiver_users = models.ManyToManyField(
        app_settings.AUTH_USER_MODEL,
        blank=True,
        verbose_name=_('Receiver_Users'),
        help_text=_('Users that are related to this subscription.'),
        # related_name='nyt_subscription',
    )

    trigger = models.ForeignKey(
        Trigger,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        help_text=_('A Trigger that is related to this subscription.'),
    )

    enabled = models.BooleanField(default=True, help_text=("If It's disabled, Subscription will be ignored"))

    def __str__(self):
        return '[Trigger: {}] , [Backends: {}]'.format(
            self.trigger,
            "{}".format(str([backend.messenger for backend in self.backends.all()]))
        )

    @property
    def subscribers(self):
        subscriber_users = self.receiver_users.all()
        for group in self.receiver_groups.all():
            subscriber_users |= group.user_set.all()
        return subscriber_users


# Todo: implement it
# @classmethod
# def get_by_key(cls, key, content_type=None):
# 	if key in _notification_type_cache:
# 		return _notification_type_cache[key]
# 	try:
# 		nt = cls.objects.get(key=key)
# 	except cls.DoesNotExist:
# 		nt = cls.objects.create(key=key, content_type=content_type)
# 	_notification_type_cache[key] = nt
# 	return nt


# These Models are just for test
class TestModel1(models.Model):
    name = models.CharField(max_length=30)
    extra_field = models.CharField(max_length=20, default="", blank=True, null=True)

    def __str__(self):
        return self.name


class TestModel2(models.Model):
    name = models.CharField(max_length=30)
    extra_field = models.CharField(max_length=20, default="", blank=True, null=True)

    def __str__(self):
        return self.name
