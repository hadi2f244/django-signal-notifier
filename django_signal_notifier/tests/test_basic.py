from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, TransactionTestCase

from django_signal_notifier.messengers import TelegramBotMessenger, SMTPEmailMessenger, SimplePrintMessenger
from django_signal_notifier.models import TestModel1, Trigger, Backend, Subscription, BasicUser
from django.core.management import call_command

from django_signal_notifier.signals import TelegramMessageSignal, SMTPEmailSignal, SimplePrintMessengerSignal

User = get_user_model()


class SignalNotifierTestBase(TransactionTestCase):

	def def_basic_users(self):
		# Todo: Erase my telegram id!
		self.user1 = BasicUser(first_name="hadi",
		                  last_name="azaddel",
		                  email="hadi2f2@gmail.com",
		                  username="hazdl",
		                  telegram_chat_id="78067664")
		self.user1.save()

	def init_simple_messenger_check_signal(self):
		self.simple_messenger_signal_was_called = False
		self.simple_messenger_response = None
		self.simple_messenger_sender = None
		self.simple_messenger_users = None
		self.simple_messenger_context = None
		self.simple_messenger_kwargs = None

		def simple_messenger_message_handler(response, sender ,users ,context, **kwargs):
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
			self.simple_messenger_response = response
			self.simple_messenger_sender = sender
			self.simple_messenger_users = users
			self.simple_messenger_context = context
			self.simple_messenger_kwargs = kwargs

		self.simple_messenger_message_handler = simple_messenger_message_handler
		SimplePrintMessengerSignal.connect(self.simple_messenger_message_handler, sender=SimplePrintMessenger)

	def setUp(self):
		super(SignalNotifierTestBase, self).setUp()

		Trigger.reconnect_all_triggers()

		self.User = get_user_model()
		# self.testdate = datetime(2000, 1, 1)
		# self.timesince = timesince(self.testdate).encode('utf8').replace(
		#     b'\xc2\xa0', b' ').decode()
		self.group_ct = ContentType.objects.get_for_model(Group)

		self.group1 = Group.objects.create(name='group1')
		self.group2 = Group.objects.create(name='group2')

		self.user2 = self.User.objects.create_superuser('admin', 'admin@test.com', 'admin')
		self.user3 = self.User.objects.create_user('user1', 'user1@test.com')

		self.user2.groups.add(self.group1)
		self.user3.groups.add(self.group2)

		self.def_basic_users()
		self.init_simple_messenger_check_signal()

	# self.testModel1 = TestModel1.objects.create(name='test_model1', extra_field='extra')
	#
	# print(Trigger.objects.all()[0])

	def tearDown(self):
		self.user1.delete()
		self.user2.delete()
		self.user3.delete()
		super(SignalNotifierTestBase, self).tearDown()
