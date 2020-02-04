from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import Group, User, PermissionsMixin, AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.template.loader import *
from django.utils.translation import gettext_lazy as _
from django_signal_notifier.message_templates import message_template_names, get_message_template_from_string
from django_signal_notifier.messengers import get_messenger_from_string, messenger_names
from . import settings as app_settings

django_default_signal_list = [
    "pre_init",
    "post_init",
    "pre_save",
    "post_save",
    "pre_delete",
    "post_delete",
    "m2m_changed",
    "pre_migrate",
    "post_migrate",
]


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
    ##### action_object = GenericForeignKey("action_object_content_type", "action_object_id")

    # Activity Actor_Object:
    actor_object_content_type = models.ForeignKey(ContentType, blank=True, null=True, related_name='actor_object',
                                                  on_delete=models.CASCADE, db_index=True)
    actor_object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    ##### actor_object = GenericForeignKey('actor_object_content_type', 'actor_object_id')

    enabled = models.BooleanField(default=True, help_text=("To enable and disable the trigger"))

    @property
    def action_object(self):
        '''
        Due to the way GenericForeignKey is implemented, we cannot use such fields directly with filters.
        Hence we completely ignore GenericForeignKey and wrote action_object as a property.
        :return:
            1. None :
                action_object_content_type is none OR an error occurred
            2. Model :
                action_object_content_type is not none but action_object_id is none
            3. object (Model instance):
                both action_object_content_type and action_object_id aren't none
        '''
        if self.action_object_content_type is None:
            return None

        if self.action_object_id is None:
            return self.action_object_content_type.model_class()
        else:
            try:
                return self.action_object_content_type.model_class().objects.get(pk=self.action_object_id)
            except ObjectDoesNotExist:
                print("Error: Can't obtain action_object with action_object_content_type and action_object_id, "
                      "It may be deleted")
                return None  # Todo: returning None may cause future errors

    @property
    def actor_object(self):
        '''
            Same as action_object property but provided for actor_object
        '''
        if self.actor_object_content_type is None:
            return None

        if self.actor_object_id is None:
            return self.actor_object_content_type.model_class()
        else:
            try:
                return self.actor_object_content_type.model_class().objects.get(pk=self.actor_object_id)
            except ObjectDoesNotExist:
                print("Error: Can't obtain actor_object with actor_object_content_type and actor_object_id, "
                      "It may be deleted")
                return None  # Todo: returning None may cause future errors

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

        action_object = signal_kwargs.pop('instance',
                                          signal_kwargs.pop('sender', None))

        # Making sure that instance class equals sender to avoid future issues
        instance = signal_kwargs.pop('instance', None)
        sender = signal_kwargs.pop('sender', None)
        if (sender is not None) and (instance is not None):
            instance_contenttype = ContentType.objects.get_for_model(instance.__class__)
            sender_contenttype = ContentType.objects.get_for_model(sender)
            if instance_contenttype != sender_contenttype:
                print("Error: instance(" + str(instance_contenttype) + ") and sender" + str(sender_contenttype) + \
                      ") are from different class. Custom signal doesn't provided properly.")
                print("Related trigger details: ", self)

        # Find value of each activity's attribute(action_object, actor_object and target)
        actor_object = signal_kwargs.pop('actor_object', None)
        target = signal_kwargs.pop('target', None)

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
        if (self.action_object_content_type == None or (
                action_object_content_type == self.action_object_content_type)) and \
                (self.actor_object_content_type == None or (
                        actor_object_content_type == self.actor_object_content_type)) and \
                (self.target is None or self.target == "" or (target == self.target)):

            # If action_object_id is None, it means action_object is a class not an object, So does actor.
            if (self.action_object_id == None or (self.action_object_id == action_object_id)) and \
                    (self.actor_object_id == None or (self.action_object_id == actor_object_id)):
                return True

        return False

    def get_verb_signal(self):
        try:
            return Trigger.verb_signal_list[self.verb]
        except KeyError:
            print("Error on getting verb signal (There isn't any inited signal name ", self.verb, ")")
            return None

    # Note: Do we need it ?!
    @classmethod
    def disconnect_all_triggers(cls):
        for trigger in Trigger.objects.all():
            trigger.disconnect_trigger_signal()

    def disconnect_trigger_signal(self):
        """
            Before changing or deleting a Trigger, We must disconnect related handler and signal from each other.
            Because signals aren't weakref so we must disconnect them manually
            to avoid invalid handler in future(bounded function or handler that is related to the deleted trigger)
            related issue:
                https://stackoverflow.com/questions/1110668/why-does-djangos-signal-handling-use-weak-references-for-callbacks-by-default
        """

        prev_self = Trigger.objects.get(pk=self.id)  # get previous version of trigger
        verb_signal = prev_self.get_verb_signal()
        if verb_signal is None:
            print("Disconnecting trigger failed! Can't find verb_signal")
            return

        for receiver in verb_signal.receivers:
            try:
                if receiver[1].__self__ != self:
                    # For example post_save connected to another handler out of DSN
                    print(
                        "Receiver's bounded method is not handler function of a trigger, So DSN doesn't disconnect it "
                        "from the signal")
                    continue
            except AttributeError:
                print("Receiver's bounded method is not handler function of a trigger, So DSN doesn't disconnect it "
                      "from the signal")
                continue

            if self.action_object_content_type is not None:
                # Make sure that is disconnected completely from new and old object to avoid unplanned problems
                prev_action_object_content_type_class = None
                if prev_self.action_object_content_type is not None:
                    prev_action_object_content_type_class = prev_self.action_object_content_type.model_class()
                disconnectedSuccess = verb_signal.disconnect(receiver=prev_self,
                                                             sender=prev_action_object_content_type_class,
                                                             dispatch_uid=str(prev_self)) or \
                                      verb_signal.disconnect(receiver=self,
                                                             sender=self.action_object_content_type.model_class(),
                                                             dispatch_uid=str(self))
            else:
                # Make sure that is disconnected completely from new and old object to avoid unplanned problems
                disconnectedSuccess = verb_signal.disconnect(receiver=prev_self,
                                                             sender=None,
                                                             dispatch_uid=str(prev_self)) or \
                                      verb_signal.disconnect(receiver=self,
                                                             sender=None,
                                                             dispatch_uid=str(self))
            if not disconnectedSuccess:
                print("Disconnecting failed! Details:")
                print("trigger: ", self)
                print("verb_signal: ", verb_signal)

    @classmethod
    def create_all_triggers(cls, signal):
        # ???????
        triggers = cls.objects.get_or_create(
            key=signal.__name__,
        )

    def save(self, *args, **kwargs):
        reconnectHandlerAfterEdit = False
        if self.pk is not None:  # Disconnecting the handler from the old trigger
            self.disconnect_trigger_signal()
            reconnectHandlerAfterEdit = True
        super(Trigger, self).save(*args, **kwargs)

        if reconnectHandlerAfterEdit:
            self.reconnect_trigger()  # Reconnecting the handler to the changed trigger's handler

    @classmethod
    def save_by_model(cls, verb_name, enabled=True, action_object=None, actor_object=None, target=None, trigger_obj=None):
        """
        Create a Trigger for an Activity and connect the verb_signal to the Trigger.handler
        Differences with save() function: Here we don't have content_type,
        So we first retrieve content_types from actor_object and action_object then create or save the trigger

        :param verb_name: string, activity verb, It usually is the name of the signal
        :param enabled: bool, status of the trigger
        :param target: string, activity target
        :param action_object: object or model, activity action_object
        :param actor_object: object or model, activity actor_object
        :param trigger_obj: Trigger model, sometimes we access to the trigger object and we just want to change it.
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

        if trigger_obj is None:
            # Trigger Creation
            # at first time, it should be created and just be get for next time
            # So make sure that get_or_create works properly
            try:
                trigger_obj = cls.objects.get_or_create(
                    verb=verb_name,
                    enabled=enabled,
                    action_object_content_type=action_object_content_type,
                    action_object_id=action_object_id,
                    actor_object_content_type=actor_object_content_type,
                    actor_object_id=actor_object_id,
                    target=target, )[0]
                # if action_object_content_type:
                #     verb_signal.connect(trigger.handler, sender=action_object_class, dispatch_uid=str(trigger),
                #                         weak=False)
                # else:
                #     verb_signal.connect(trigger.handler, sender=None, dispatch_uid=str(trigger),
                #                         weak=False)
                # return trigger
            except ObjectDoesNotExist as e:
                # raise IntegrityError("Subscription already made\nError message: {}".format(e))
                print("Exception: ", e)
        else:
            trigger_obj.verb = verb_name
            trigger_obj.enabled = enabled
            trigger_obj.action_object_content_type = action_object_content_type
            trigger_obj.action_object_id = action_object_id
            trigger_obj.actor_object_content_type = actor_object_content_type
            trigger_obj.actor_object_id = actor_object_id
            trigger_obj.target = target
        trigger_obj.save()
        return trigger_obj

    @classmethod
    def init_verb_signal(cls, verb_name, verb_signal):
        """
            Each custom signal(non pre-defined signal like pre_save) must be introduced to DSN in each running
            It must be done in ready function in apps.py before calling reconnect_all_triggers.
        :param verb_name: String,
        :param verb_signal: Signal,
        """
        if verb_name in cls.verb_signal_list:
            raise ValueError("A signal with same name has already existed.")
        else:
            cls.verb_signal_list[verb_name] = verb_signal
        # for trigger in cls.objects.filter(verb=verb_name):
        #     if trigger.action_object_content_type is not None:
        #         verb_signal.connect(trigger.handler, sender=trigger.action_object_content_type.model_class(),
        #                             dispatch_uid=str(trigger), weak=False)
        #     else:
        #         verb_signal.connect(trigger.handler, sender=None,
        #                             dispatch_uid=str(trigger), weak=False)

    # Initialize default signal list
    @classmethod
    def add_verb_signal_list(cls, verb_signal_list):
        for verb_name in verb_signal_list:
            cls.verb_signal_list[verb_name] = verb_signal_list[verb_name]

    def reconnect_trigger(self):
        if not self.enabled:
            print("This signal is disabled. details: ", self)
            return

        verb_signal = self.get_verb_signal()
        if verb_signal is None:
            print("Reconnecting trigger failed! Can't find verb_signal")
            return

        if self.action_object_content_type is not None:
            verb_signal.connect(self.handler, sender=self.action_object_content_type.model_class(),
                                dispatch_uid=str(self), weak=False)
        else:
            verb_signal.connect(self.handler, sender=None,
                                dispatch_uid=str(self), weak=False)

    @classmethod
    # Todo: write a test for this function(It's not usual because we should rerun the app completely to check its functionality)
    def reconnect_all_triggers(cls):
        for trigger in cls.objects.all():
            trigger.reconnect_trigger()

    def clean(self):
        if (self.action_object_content_type is not None) and (self.action_object_id is not None):
            try:
                action_object = self.action_object_content_type.model_class().objects.get(
                    pk=int(self.action_object_id))
            except ObjectDoesNotExist:
                raise ValidationError("Error: Can't find any object (action_object) with this id equals " +
                                      str(self.action_object_id) +
                                      " for " + str(self.action_object_content_type.model_class()))

        if (self.actor_object_content_type is not None) and (self.actor_object_id is not None):
            try:
                actor_object = self.actor_object_content_type.model_class().objects.get(
                    pk=int(self.actor_object_id))
            except ObjectDoesNotExist:
                raise ValidationError("Error: Can't find any object (actor_object) with this id equals " +
                                      str(self.actor_object_id) +
                                      " for " + str(self.actor_object_content_type.model_class()))

        # Check trigger duplication:
        for trigger in Trigger.objects.all():
            if trigger.id != self.id:
                if trigger.action_object_content_type == self.action_object_content_type and \
                        trigger.action_object_id == self.action_object_id and \
                        trigger.actor_object_content_type == self.actor_object_content_type and \
                        trigger.actor_object_id == self.actor_object_id and \
                        trigger.verb == self.verb and \
                        trigger.target == self.target:
                    raise ValidationError("Duplicate Trigger")

        if self.verb in django_default_signal_list:
            if self.action_object_content_type is None:
                raise ValidationError("Django default signals aren't valid without action_object(sender)")

    def run_corresponding_signal(self, **signal_kwargs):
        '''
        This function is provided for testing manually.
        It uses default signal parameters. You add some arguments same as arguments of signal handlers.
        We get sender and instance arguments from trigger itself regardless of signal_kwargs

        Note: Running corresponding signal cause correlative triggers run too.
        '''

        verb_signal = self.get_verb_signal()
        if self.action_object_id is None:
            verb_signal.send(sender=signal_kwargs.pop('sender', self.action_object),
                             instance=signal_kwargs.pop('instance', None),
                             actor_object=signal_kwargs.pop('actor_object', self.actor_object),
                             target=signal_kwargs.pop('target', self.target),
                             **signal_kwargs)

            print(f"A signal sent by : \n",
                  f" signal={self.verb} \n",
                  f" sender={signal_kwargs.pop('sender', self.action_object)} \n",
                  f" instance={signal_kwargs.pop('instance', None)} \n",
                  f" actor_object={signal_kwargs.pop('actor_object', self.actor_object)} \n",
                  f" target={signal_kwargs.pop('target', self.target)} \n",
                  f" **signal_kwargs={signal_kwargs}")
        else:
            # verb_signal.send(sender=self.action_object_content_type.model_class(), instance=self.action_object,
            # actor_object=self.actor_object, target=self.target, **signal_kwargs)
            verb_signal.send(sender=signal_kwargs.pop('sender', self.action_object_content_type.model_class()),
                             instance=signal_kwargs.pop('instance', self.action_object),
                             actor_object=signal_kwargs.pop('actor_object', self.actor_object),
                             target=signal_kwargs.pop('target', self.target),
                             **signal_kwargs)
            print(f"A signal sent by : \n",
                  f" signal={self.verb} \n",
                  f" sender={signal_kwargs.pop('sender', self.action_object_content_type.model_class())} \n",
                  f" instance={signal_kwargs.pop('instance', self.action_object)} \n",
                  f" actor_object={signal_kwargs.pop('actor_object', self.actor_object)} \n",
                  f" target={signal_kwargs.pop('target', self.target)} \n",
                  f" **signal_kwargs={signal_kwargs}) \n")


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

    enabled = models.BooleanField(default=True, help_text=("To enable and disable the subscription"))

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
