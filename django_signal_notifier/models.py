import json

from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import pre_save
from django.template.loader import *
from django.utils.translation import gettext_lazy as _
from django_signal_notifier import settings
from django_signal_notifier.message_templates import message_template_names, get_message_template_from_string
from django_signal_notifier.messengers import get_messenger_from_string, messenger_names
from django.db.utils import IntegrityError

#
# class MessageTemplate(models.Model):
# 	"""
# 	MessageTemplate model to customize messages sent to users via Backends.
# 	text is a static text that is formatted via params given in  context field.
# 	"""
# 	name = models.CharField(
# 		max_length = 128,
# 		default = "BaseMessageTemplate",
# 		choices = message_template_names,
# 	)
#
# 	def render(self, context=None):
# 		templateMessageClass = get_message_template_from_string(self.name)
# 		if templateMessageClass is not None:
# 			templateMessage = templateMessageClass()
# 			return templateMessage.render(context)
# 		else:
# 			print("Can't any message_template with this name")
# 			raise ValueError("Can't any message_template with this name")
#
# 	def __str__(self):
# 		return self.name


class Backend(models.Model):
	"""
	Backend used to send messages
	"""

	# Todo: Create fixtures to initialize messenger backends
	messenger = models.CharField(  # use it instead of  ModelSignal tentatively
		max_length=128,
		default="BaseMessanger",
		choices=messenger_names,
	)

	message_template = models.CharField(
		max_length = 128,
		default = "BaseMessageTemplate",
		choices = message_template_names,
	)

	def send_message(self, sender, users, context, **kwargs):
		messengerClass = get_messenger_from_string(self.messenger)
		if messengerClass is not None:
			templateMessageClass = get_message_template_from_string(self.message_template)
			if templateMessageClass is not None:
				templateMessage = templateMessageClass()
				msngr = messengerClass()
				msngr.send(templateMessage, sender, users, context, **kwargs)
			else:
				print("Can't any message_template with this name")
				raise ValueError("Can't any message_template with this name")
		else:
			print("Can't any messenger with this name")
			raise ValueError("Can't any messenger with this name")

	def __str__(self):
		return self.messenger + " Backend with " + self.message_template


class Trigger(models.Model):
	"""	contains signal from specific sender. Actually is a activity accrued by the signal"""

	# Activity Verb:
	# todo: implement a djagno db field that save these, use that signal name

	verb_signal_list = {}  # Used to map signal name(verb_name) to signal(verb_signal),
	# must be set in apps.py by set_verb_signal_list or add_verb_signal

	# ?????
	verb = models.CharField(  # use it instead of  ModelSignal tentatively
		max_length=128,
		db_index=True,
	)

	# Activity Action_Object:

	action_object_content_type = models.ForeignKey(ContentType, blank=True, null=True, related_name='action_object',
	                                               on_delete=models.CASCADE, db_index=True)
	action_object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
	action_object = GenericForeignKey("action_object_content_type", "action_object_id")

	# Activity Actor:

	actor_object_content_type = models.ForeignKey(ContentType, blank=True, null=True, related_name='actor_object',
	                                              on_delete=models.CASCADE, db_index=True)
	actor_object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
	actor_object = GenericForeignKey('actor_object_content_type', 'actor_object_id')

	# Activity Target:  # use it instead of  ModelSignal tentatively
	target = models.CharField(max_length=128, blank=True, null=True, db_index=True)

	# Todo: Each signal has its own arguments, So we should save those arguments and send them to the subcription hadnler,
	# So, By a field (that can be named signal_extra_args) we can provide it for different signal to implement their own extra arguments
	# It should be set on register_signal function(e.g. post_save has an extra argument named instance)
	# signal_extra_args =

	def __str__(self):
		return 'Verb: {} , Action object: {} , Actor object: {} , Target: {}'.format(
			self.verb,
			"{}:{}".format(self.action_object_content_type,
			               "instance(pk = {})".format(self.action_object_id)
			               if self.action_object_id is not None and self.action_object_id != "" else "Model itself")
			if (self.action_object_content_type is not None and self.action_object_content_type != "") else _("Something"),
			"{}:{}".format(self.actor_object_content_type,
			               "Instance of model(pk = {})".format(self.actor_object_id)
			               if self.actor_object_id is not None and self.actor_object_id != "" else "Model itself")
			if (self.actor_object_content_type is not None and self.actor_object_content_type != "") else _("All"),
			self.target if (self.target is not None and self.target != "") else _("SomeWhere!")
		)

	def handler(self, sender, **kwargs):
		if self.match_signal_trigger(sender, **kwargs):  # Todo: what to do with different backends?!
			all_subscriptions = self.subscriptions.all()
			context = dict(action_object=self.action_object,
			               action_object_content_type=self.action_object_content_type,
			               actor_object=self.actor_object,
			               actor_object_content_type=self.actor_object_content_type,
			               verb=self.verb,
			               target=self.target,
			               subscribers=[u.username for s in all_subscriptions for u in s.subscribers.all()]
			               )
			for subscription in all_subscriptions:
				for backend in subscription.backends.all():
					backend.send_message(sender, subscription.subscribers.all(), context, **kwargs)

	def match_signal_trigger(self, sender, **kwargs):
		"""
		Check trigger parameters and the signal then calls it if their match their selves
		self.verb checked by trigger
		Trigger parameters are :
		self.action_object_content_type
		self.action_object_object_ids
		self.actor_object_id
		self.actor_content_type
		self.target
		:return: Boolean
		"""

		action_object = kwargs.pop('instance', sender)
		# sender is action_object class, but you can use action_object to access specific instance

		actor = kwargs.pop('actor', None)
		target = kwargs.pop('target', None)

		action_object_class = action_object
		action_object_object_pk = None
		if type(action_object.pk) != property:  # It's not a model, It's an object(model instance)
			action_object_class = action_object.__class__
			action_object_object_pk = action_object.pk

		action_object_class_content_type = ContentType.objects.get_for_model(action_object_class)

		if actor is not None:
			actor_class = actor
			actor_object_pk = None
			if type(actor.pk) != property:  # It's not a model, It's an object(model instance)
				actor_class = actor.__class__
				actor_object_pk = actor.pk
			actor_class_content_type = ContentType.objects.get_for_model(actor_class)
		else:
			actor_class_content_type = None
			actor_object_pk = None

		if action_object_class_content_type == self.action_object_content_type and \
				action_object_object_pk == self.action_object_id and \
				actor_class_content_type == self.actor_object_content_type and \
				actor_object_pk == self.actor_object_id and \
				target == self.target:

			return True
		else:
			return False

	@classmethod
	def create_signal(cls, actor, action, verb, target):
		pass

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
	def register_trigger(cls, verb_name, action_object, actor=None, target=None):
		"""
		Create a Trigger for an Activity and connect the verb_signal to the Trigger.handler

		:param verb_name: string, activity verb, It usually is the name of the signal
		:param target: string, activity target
		:param action_object: object or model, activity action_object
		:param actor: object or model, activity actor
		:return: None
		"""

		# verb_signal: ModelSignal, a signal that we want connect it the Trigger.handler method
		if verb_name in cls.verb_signal_list:
			verb_signal = cls.verb_signal_list[verb_name]  # Get signal function from verb_signal_list
		else:
			raise ValueError("verb_name must be add first to Trigger.verb_signal_list(use add_verb_signal()"
			                 " or set_verb_signal_list())")

		action_object_class = action_object
		action_object_object_pk = None
		if type(action_object.pk) != property:  # It's not a model, It's an object(model instance)
			action_object_class = action_object.__class__
			action_object_object_pk = action_object.pk

		action_object_class_content_type = ContentType.objects.get_for_model(action_object_class)

		if actor is not None:
			actor_class = actor
			actor_object_pk = None
			if type(actor.pk) != property:  # It's not a model, It's an object(model instance)
				actor_class = actor.__class__
				actor_object_pk = actor.pk
			actor_class_content_type = ContentType.objects.get_for_model(actor_class)
		else:
			actor_class_content_type = None
			actor_object_pk = None

		# Trigger Creation
		# ToDo: Because register_trigger run in each startup, trigger should connect to signals on every startup,
		# at first time, it should be created and just be get for next time
		# So make sure that get_or_create works properly
		try:
			trigger = cls.objects.get_or_create(
				verb=verb_name,
				action_object_content_type=action_object_class_content_type,
				action_object_id=action_object_object_pk,
				actor_object_content_type=actor_class_content_type,
				actor_object_id=actor_object_pk,
				target=target, )[0]
			verb_signal.connect(trigger.handler, dispatch_uid=str(trigger), weak=False)
			return trigger
		except Exception as e:
			# raise IntegrityError("Subscription already made\nError message: {}".format(e))
			print("Exception: ", e)
		# connect verb_signal to Trigger.handler

	@classmethod
	def add_verb_signal(cls, verb_name, verb_signal):
		cls.verb_signal_list[verb_name] = verb_signal

	@classmethod
	def set_verb_signal_list(cls, verb_signal_list):
		cls.verb_signal_list = verb_signal_list

	@classmethod
	def reconnect_all_triggers(cls):
		# Todo: We connect the signals to the handler correctly, but the signal calls the handler more than one time, We guess that it's relared to djagno itself
		for trigger in cls.objects.all():
			signal = cls.verb_signal_list[trigger.verb]
			signal.connect(trigger.handler, dispatch_uid=str(trigger), weak=False)
		# print(signal)


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


# def register_signal(signal):  # ModelSignal
# 	pass
#
#

class BasicUser(User):
	telegram_chat_id = models.CharField(max_length=20, blank=True, null=True)

	def __str__(self):
		return self.first_name + " " + self.last_name + "\n@" + self.username


class Subscription(models.Model):
	# backends = GM2MField( #Todo: Check performance of GM2MField
	# 	verbose_name=_('Backend'),
	# 	blank = True,
	# 	help_text=_('Backend that specified for this subscription.'),
	# )
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
		BasicUser,
		blank=True,
		verbose_name=_('Receiver_Users'),
		help_text=_('Users that are related to this subscription.'),
		# related_name='nyt_subscription',
	)

	trigger = models.ForeignKey(
		Trigger,
		related_name="subscriptions",
		on_delete=models.CASCADE,
		help_text=_('Trigger that is related to this subscription.'),
	)

	def __str__(self):
		return "Trigger: pk={} ,".format(self.trigger.pk) + "Backends: " + str([backend.name for backend in self.backends.all()])

	# class Meta:
	# 	db_table = settings.DB_TABLE_PREFIX + '_subscription'
	# 	verbose_name = _('subscription')
	# 	verbose_name_plural = _('subscriptions')

	@property
	def subscribers(self):
		# Todo: imporove this if possible!
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

class TestModel(models.Model):
	name = models.CharField(max_length=30)
	extra_field = models.CharField(max_length=20, default="", blank=True, null=True)

	def __str__(self):
		return self.name


class TestModel2(models.Model):
	name = models.CharField(max_length=30)
	extra_field = models.CharField(max_length=20, default="", blank=True, null=True)

	def __str__(self):
		return self.name
