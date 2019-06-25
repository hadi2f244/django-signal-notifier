from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_save
from django.utils.translation import gettext_lazy as _
from gm2m import GM2MField

from django_signal_notifier.messengers import get_messenger_from_string, Messengers_name


class Message():
	sender = None
	message_template = "%s: %s"
	kwargs = None

	def get_message(self):  # Todo: Use each object(model or sender) __str__ object
		return self.message_template % (self.sender, self.kwargs)

# def get_name(variable):
# 	return [k for k, v in locals().items() if v == variable][0]

class Backend(models.Model):
	'''
	Backend used to send messages
	'''
	name = models.CharField(  # use it instead of  ModelSignal tentatively
		max_length=128,
		default="BaseMessanger",
		unique = True,
		choices=Messengers_name,
	)

	# class Meta:
	# 	abstract = True
	def send_message(self):
		Messenger = get_messenger_from_string(self.name)
		if Messenger != None:
			messenger = Messenger()
			messenger.send()
		else:
			print("Can't any messenger with this name")


# class SimplePrintMessageBackend(Backend):
# 	def send_message(self, message):
# 		print(message.get_message())


class Trigger(models.Model):
	'''
	contains signal from specific sender. Actually is a activity accrued by the signal
	'''

	# Activity Verb:
	# todo: implement a djagno db field that save these, use that signal name
	# signal = ModelSignal
	verb = models.CharField(  # use it instead of  ModelSignal tentatively
		max_length=128,
		db_index=True,
	)

	# Activity Action_Object:
	action_object_content_type = models.ForeignKey(
		ContentType, blank=True, null=True,
		related_name='action_object',
		on_delete=models.CASCADE, db_index=True
	)
	action_object_object_id = models.CharField(
		max_length=255, blank=True, null=True, db_index=True
	)
	# action_object = GenericForeignKey(
	# 	'action_object_content_type',
	# 	'action_object_object_id'
	# )

	# Activity Actor:
	actor_content_type = models.ForeignKey(
		ContentType, blank=True, null=True,
		related_name='actor',
		on_delete=models.CASCADE, db_index=True
	)
	actor_object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
	# actor = GenericForeignKey('actor_content_type', 'actor_object_id')

	# Activity Target:
	target = models.CharField(  # use it instead of  ModelSignal tentatively
		max_length=128,
		db_index=True,
	)

	def __str__(self):
		return '{} {} {} on {}'.format(
			"{}:{}".format(self.actor_content_type , self.actor_object_id)
				if (self.actor_content_type!=None or self.actor_content_type!="") else _("Someone"),
			self.verb,
			"{}:{}".format(self.action_object_content_type,self.action_object_object_id)
				if (self.action_object_content_type!=None or self.action_object_content_type!="") else _("Something"),
			self.target if (self.target!=None or self.target!="") else _("SomeWhere!"),
		)

	# class Meta:
	# 	db_table = settings.DB_TABLE_PREFIX + '_trigger'
	# 	verbose_name = _('Trigger')
	# 	verbose_name_plural = _('Trigger')

	# check ReferenceError: weakly-referenced object no longer exists
	# https://mindtrove.info/python-weak-references/
	# @classmethod
	def handler(self, sender, **kwargs):
		# print(sender)
		# print(kwargs)
		# print("verb:    ",self.verb)
		# print(self.subscription)
		for backend in self.subscription.backends.all():
			backend.send_message()

	@classmethod
	def disconnect_all_triggers(cls):
		pass

	@classmethod
	def create_all_triggers(cls, signal):
		triggers = cls.objects.get_or_create(
			key=signal.__name__,
		)
		# Get all of models in project
		pre_save()
		# Connect
		# signal.connect(trigger.handler, dispatch_uid=signal.__name__)

	@classmethod
	def register_trigger(cls, verb_name, verb_signal, target,
	                     action_object, actor):
		'''
		Create a Trigger for an Activity and connect the verb_signal to the Trigger.handler

		:param verb_name: string, activity verb, It usually is the name of the signal
		:param verb_signal: ModelSignal, a signal that we want connect it the Trigger.handler method
		:param target: string, activity target
		:param action_object: object or model, activity action_object
		:param actor: object or model, activity actor
		:return: None
		'''

		action_object_class = action_object
		action_object_object_pk = None
		if type(action_object.pk) != property: # It's not a model, It's an object(model instance)
			action_object_class = action_object.__class__
			action_object_object_pk = action_object.pk

		actor_class = actor
		actor_object_pk = None
		if type(actor.pk) != property :  # It's not a model, It's an object(model instance)
			actor_class = actor.__class__
			actor_object_pk = actor.pk

		# Trigger Creation
		# ToDo: Because register_trigger run in each startup, trigger should connect to signals on everystartup,
		#  at first time, it should be created and just be get for next time, So make sure that get_or_create works properly
		trigger = cls.objects.get_or_create(
			verb=verb_name,
		    action_object_content_type = ContentType.objects.get_for_model(action_object_class),
			action_object_object_id = action_object_object_pk,
			actor_content_type = ContentType.objects.get_for_model(actor_class),
			actor_object_id= actor_object_pk,
			target = target,
		)[0]
		Subscription.objects.create(trigger=trigger)
		# connect verb_signal to Trigger.handler
		verb_signal.connect(trigger.handler, dispatch_uid=str(trigger), weak=False)

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
		help_text=_('Backend that specified for this subscription.'),
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
		User,
		blank=True,
		verbose_name=_('Receiver_Users'),
		help_text=_('Users that are related to this subscription.'),
		# related_name='nyt_subscription',
	)

	trigger = models.OneToOneField(
		to=Trigger,
		on_delete=models.CASCADE,
		verbose_name=_('Trigger'),
		help_text=_('Trigger that is related to this subscription.'),
	)


	def __str__(self):
		subscribers_usernames = [getattr(user, user.USERNAME_FIELD) for user in self.subscribers]
		obj_name = _("Subscription for: %s") % subscribers_usernames
		return obj_name

	# class Meta:
	# 	db_table = settings.DB_TABLE_PREFIX + '_subscription'
	# 	verbose_name = _('subscription')
	# 	verbose_name_plural = _('subscriptions')

	@property
	def subscribers(self):
		# Todo: imporove this if possible!
		subscriber_users = self.receiver_users.all()
		for group in  self.receiver_groups.all():
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
