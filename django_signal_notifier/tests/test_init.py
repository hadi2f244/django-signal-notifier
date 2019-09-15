from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, TransactionTestCase

from django_signal_notifier.messengers import TelegramBotMessenger, SMTPEmailMessenger, SimplePrintMessenger, SimplePrintMessengerTemplateBased
from django_signal_notifier.models import TestModel1, Trigger, Backend, Subscription, BasicUser, TestModel2
from django.core.management import call_command

from django_signal_notifier.signals import TelegramMessageSignal, SMTPEmailSignal, SimplePrintMessengerSignal, SimplePrintMessengerSignalTemplateBased

User = get_user_model()


class SignalNotifierTestBase(TransactionTestCase):



	def init_simple_messenger_check_signal(self):
		'''
		reinitialize simple messenger handler results.
		:return:
		'''
		self.simple_messenger_signal_was_called = False
		self.simple_messenger_responses = None
		self.simple_messenger_sender = None
		self.simple_messenger_users = None
		self.simple_messenger_trigger_context = None
		self.simple_messenger_signal_kwargs = None

		def simple_messenger_message_handler(sender, responses ,users ,trigger_context, signal_kwargs, **kwargs):
			"""
			this functions handles sent telegram messages. when a telegram message is sent,
			 a signal(TelegramMessegeSignal) is sent. this function receives the signal and updates test status.
			 test status is checked via assertions below.
			:param sender: sender class of the signal. In this case, the sender is TelegramBotMessenger.
			:param response: if the message is delivered this param is True.
			:param kwargs: ...
			:return:
			"""
			self.simple_messenger_signal_was_called = True
			self.simple_messenger_responses = responses
			self.simple_messenger_sender = sender
			self.simple_messenger_users = users
			self.simple_messenger_trigger_context = trigger_context
			self.simple_messenger_signal_kwargs = signal_kwargs

		self.simple_messenger_message_handler = simple_messenger_message_handler
		SimplePrintMessengerSignal.connect(self.simple_messenger_message_handler, sender=SimplePrintMessenger)
		SimplePrintMessengerSignalTemplateBased.connect(self.simple_messenger_message_handler, sender=SimplePrintMessengerTemplateBased)

	def setUp(self):
		super(SignalNotifierTestBase, self).setUp()

		Trigger.reconnect_all_triggers()

		self.User = BasicUser
		# self.group_ct = ContentType.objects.get_for_model(Group)

		self.group1 = Group.objects.create(name='group1')
		self.group2 = Group.objects.create(name='group2')

		self.user1 = BasicUser(first_name="hadi",
		                       last_name="azaddel",
		                       email="hadi2f2@gmail.com",
		                       username="hazdl",
		                       telegram_chat_id="78067664")
		self.user1.save()
		self.user2 = self.User.objects.create_superuser('admin', 'admin@test.com', 'admin')
		self.user3 = BasicUser(first_name="hadi1",
		                       last_name="azaddel1",
		                       email="hadi2f21@gmail.com",
		                       username="hazdl1",
		                       telegram_chat_id="78067664")
		self.user3.save()

		# self.group1.user_set.add(self.user1)
		# self.group2.user_set.add(self.user2)
		# self.group2.user_set.add(self.user3)
		# #
		self.user1.groups.add(self.group1)
		self.user2.groups.add(self.group2)
		self.user3.groups.add(self.group2)

		self.init_simple_messenger_check_signal()

	# self.testModel1 = TestModel1.objects.create(name='test_model1', extra_field='extra')
	#
	# print(Trigger.objects.all()[0])

	def tearDown(self):
		self.user1.delete()
		self.user2.delete()
		self.user3.delete()
		super(SignalNotifierTestBase, self).tearDown()



	def test_save_trigger_actionObject_class_template(self, signal_name, messenger, message_template):
		'''
			This function test register a trigger by pre_save as verb(signal) and TestModel1 as action_object(sender)
			Then calling SimplePrintMessenger send function is test by creating a TestModel1(It called pre_save signal implicitly)

			Test Goals:
				1. SimplePrintMessenger as backend
				2. register_trigger function
				3. Subscription simple functionality
			'''

		# A. By pre_save signal

		# 1. Init:
		# 1.1: Create SimplePrintMessenger backend
		# simplePrintMessengerBackend = Backend.objects.create(messenger="SimplePrintMessenger", message_template="BaseMessageTemplate")
		simplePrintMessengerBackend = Backend.objects.create(messenger=messenger, message_template=message_template)

		# 1.2: Register a trigger by pre_save as verb(signal) and TestModel1 as action_object(sender)
		trigger_preSave_TestModel = Trigger.register_trigger(
			verb_name=signal_name,
			action_object=TestModel1,
		)

		# 1.3: Create a subscription
		subscription_preSave_TestModel = Subscription.objects.create(trigger=trigger_preSave_TestModel)
		subscription_preSave_TestModel.backends.add(simplePrintMessengerBackend)
		subscription_preSave_TestModel.receiver_users.add(self.user1)

		# 2. Test:
		# 2.1: Must call on TestModel1 pre_save
		self.init_simple_messenger_check_signal()
		TestModel1.objects.create(name="new_test_model1", extra_field="extra")

		self.assertTrue(self.simple_messenger_signal_was_called)
		self.assertEqual(self.simple_messenger_trigger_context['action_object_content_type'], ContentType.objects.get_for_model(TestModel1))
		self.assertEqual(self.simple_messenger_trigger_context['verb'], signal_name)

		# 2.2: Must not call on TestModel2 pre_save
		self.init_simple_messenger_check_signal()
		TestModel2.objects.create(name="new_test_model1", extra_field="extra")
		self.assertFalse(self.simple_messenger_signal_was_called)
