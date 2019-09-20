import time

from django_signal_notifier.message_templates import SimplePrintMessageTemplate
from django_signal_notifier.messengers import SMTPEmailMessenger, TelegramBotMessenger
from django_signal_notifier.models import *
from django_signal_notifier.signals import TelegramMessageSignal, SMTPEmailSignal
from django_signal_notifier.tests.test_init import SignalNotifierTestBase


class TriggerTestCase(SignalNotifierTestBase):

# message_template:
	def test_template_render(self):
		base_message_template = SimplePrintMessageTemplate()

		# Initialize user, trigger_contex and signal_kwargs
		testModel1_instance = TestModel1.objects.create(name="new_test_model1", extra_field="extra")
		testModel1_Content_Type = ContentType.objects.get_for_model(TestModel1)
		basicUser_instance = self.user3
		basicUser_Content_Type = ContentType.objects.get_for_model(BasicUser)
		verb = "custom_signal"
		target = "view_example"

		subscriber = self.user1 # user
		trigger_context_example = dict(action_object=testModel1_instance,
		                       action_object_content_type=testModel1_Content_Type,
		                       actor_object=basicUser_instance,
		                       actor_object_content_type=basicUser_Content_Type,
		                       verb=verb,
		                       target=target,
		                       )
		signal_kwargs_example = dict(custom_signal_parameter = "created_by_test_function")

		# Rendering:
		rendered_text = base_message_template.render(user=subscriber, trigger_context=trigger_context_example, signal_kwargs=signal_kwargs_example)
		rendered_text.strip()
		expected_rendered_text = \
		"<div><p>verb: custom_signal</p></div>\n" + \
		"<div><p>action_object: new_test_model1</p></div>\n" + \
		"<div><p>actor_object: hadi1 azaddel1\n" + \
		"@hazdl1</p></div>\n" + \
		"<div><p>target: view_example</p></div>\n\n"

		self.assertEqual(rendered_text, expected_rendered_text)

	def test_template_based_save_trigger_actionObject_class(self):
		self.test_save_trigger_actionObject_class_template(signal_name='pre_save', messenger="SimplePrintMessengerTemplateBased", message_template="SimplePrintMessageTemplate")


# Messenger functionality:

	def init_telegram_messenger_check_signal(self):
		self.telegram_signal_was_called = False
		self.telegram_responses = None

		def telegram_message_handler(sender, responses, **kwargs):
			"""
			this functions handles sent telegram messages. when a telegram message is sent,
			 a signal(TelegramMessegeSignal) is sent. this function receives the signal and updates test status.
			 test status is checked via assertions below.
			:param sender: sender class of the signal. In this case, the sender is TelegramBotMessenger.
			:param response: if the message is delivered this param is True.
			:param kwargs: ...
			:return:
			"""
			self.telegram_signal_was_called = True
			self.telegram_responses = responses

		self.telegram_message_handler = telegram_message_handler
		TelegramMessageSignal.connect(self.telegram_message_handler, sender=TelegramBotMessenger)

	def init_smtp_messenger_check_signal(self):

		self.smtp_signal_was_called = False
		self.smtp_responses = None
		def smtp_email_handler(sender, response, **kwargs):
			"""
			this function handles sent smtp emails. when an email is successfully sent a signal is sent from
			 SMTPEmailMessenger. this function handles te signal and updates test status accordingly.
			:param sender: sender class of the signal. In this case it is SMTPEmailMessenger.
			:param response: the response provided by the signal sender class
			:param kwargs: ...
			:return:
			"""
			self.smtp_signal_was_called = True
			self.smtp_responses = response
		self.smtp_email_handler = smtp_email_handler
		SMTPEmailSignal.connect(self.smtp_email_handler, sender=SMTPEmailMessenger)

	def test_telegram_backend(self):
		"""

		"""

		self.init_telegram_messenger_check_signal()
		telegram_backend = Backend.objects.create(messenger="TelegramBotMessenger")

		users = BasicUser.objects.all()
		telegram_backend.send_message(sender=None, users=users, context={})

		# Wait for telegram api to send the message.
		telegram_sleep_time = 5
		time.sleep(telegram_sleep_time)

		self.assertTrue(self.telegram_signal_was_called)
		self.assertEqual(self.telegram_responses, [True for _ in range(len(users))], msg="Check your telegram connection first.")


	def test_smtp_backend(self):
		"""

		"""

		self.init_smtp_messenger_check_signal()
		smtp_backend = Backend.objects.create(messenger="SMTPEmailMessenger")

		users = BasicUser.objects.all()
		smtp_backend.send_message(sender=None, users=users, context={})

		email_sleep_time = 10
		time.sleep(email_sleep_time)

		self.assertTrue(self.smtp_responses)
		self.assertEqual(self.smtp_responses, [True for _ in range(len(users))], msg="Check your connection to the smtp server.")