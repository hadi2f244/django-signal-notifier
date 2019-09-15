import time

from django_signal_notifier.message_templates import SimplePrintMessageTemplate
from django_signal_notifier.messengers import SMTPEmailMessenger, TelegramBotMessenger
from django_signal_notifier.models import *
from django_signal_notifier.signals import TelegramMessageSignal, SMTPEmailSignal
from django_signal_notifier.tests.test_init import SignalNotifierTestBase


class TriggerTestCase(SignalNotifierTestBase):

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

	# 	def test_register_trigger_templates(self):
	# 		"""
	# 		this test method checks sent messages when a message_template is provided via MessageTemplate model.
	# 		:return:
	# 		"""
	# 		print("BEGINNING of test_register_trigger_templates")
	# 		print("verb_name: 'pre_save'", "action_object: instance of testmodel", sep="\n")
	#
	# 		self.telegram_signal_was_called = False
	# 		self.telegram_response = None
	#
	# 		self.smtp_signal_was_called = False
	# 		self.smtp_response = False
	#
	# 		def telegram_message_handler(sender, response, **kwargs):
	# 			"""
	# 			this functions handles sent telegram messages. when a telegram message is sent,
	# 			 a signal(TelegramMessegeSignal) is sent. this function receives the signal and updates test status.
	# 			 test status is checked via assertions below.
	# 			:param sender: sender class of the signal. In this case, the sender is TelegramBotMessenger.
	# 			:param response: if the message is delivered this param is True.
	# 			:param kwargs: ...
	# 			:return:
	# 			"""
	# 			self.telegram_signal_was_called = True
	# 			self.telegram_response = response
	#
	# 		TelegramMessageSignal.connect(telegram_message_handler, sender=TelegramBotMessenger)
	#
	# 		def smtp_email_handler(sender, response, **kwargs):
	# 			"""
	# 			this function handles sent smtp emails. when an email is successfully sent a signal is sent from
	# 			 SMTPEmailMessenger. this function handles te signal and updates test status accordingly.
	# 			:param sender: sender class of the signal. In this case it is SMTPEmailMessenger.
	# 			:param response: the response provided by the signal sender class
	# 			:param kwargs: ...
	# 			:return:
	# 			"""
	# 			self.smtp_signal_was_called = True
	# 			self.smtp_response = response
	#
	# 		SMTPEmailSignal.connect(smtp_email_handler, sender=SMTPEmailMessenger)
	#
	# 		test_model1 = TestModel1.objects.create(name="new_test_model_1", extra_field="extra")
	# 		test_model2 = TestModel1.objects.create(name="new_test_model_2", extra_field="extra2")
	#
	# 		trigger = Trigger.register_trigger(
	# 			verb_name="pre_save",
	# 			action_object=test_model1,
	# 		)
	#
	# 		# email_text = "{verb_name} {object_name} {current_time}"
	#
	# 		# email_context = dict(verb_name=trigger.verb,
	# 		#                      object_name="test_model1",
	# 		#                      current_time=str(datetime.datetime.now().date()))
	# 		# email_context = json.dumps(email_context)
	# 		# email_template = MessageTemplate.objects.create(text=email_text, context=email_context)
	#
	# 		# This is an telegram message message_template which has 4 context_variables
	#
	# 		# telegram_text_1 = "{backend_name} {verb_name} {object_name} {current_time}"
	# 		# telegram_context_1 = dict(verb_name=trigger.verb,
	# 		#                           object_name="test_model1",
	# 		#                           current_time=str(datetime.datetime.now()),
	# 		#                           backend_name="backend3")
	# 		# telegram_context_1 = json.dumps(telegram_context_1)
	# 		# telegram_template_1 = MessageTemplate.objects.create(text=telegram_text_1, context=telegram_context_1)
	#
	#
	# 		# telegram_text_2 = "This is another telegram message message_template which has no context variables."
	# 		# telegram_context_2 = json.dumps(dict())
	# 		# telegram_template_2 = MessageTemplate.objects.create(text=telegram_text_2, context=telegram_context_2)
	#
	#
	# 		# base_text = "This is a message_template for base messenger."
	# 		# base_context = json.dumps(dict())
	# 		# base_template = MessageTemplate.objects.create(text=base_text, context=base_context)
	#
	#
	# 		backend1 = Backend.objects.create(messenger="BaseMessenger", message_template="BaseMessageTemplate")
	# 		backend2 = Backend.objects.create(messenger="TelegramBotMessenger", message_template="SimpleTelegramMessageTemplate1")
	# 		backend3 = Backend.objects.create(messenger="SMTPEmailMessenger", message_template = "SimpleEmailMessageTemplate")
	# 		backend4 = Backend.objects.create(messenger="TelegramBotMessenger", message_template="SimpleTelegramMessageTemplate2")
	#
	# 		subscription = Subscription.objects.create(trigger=trigger)
	# 		subscription.backends.add(backend1)
	# 		subscription.backends.add(backend2)
	# 		subscription.backends.add(backend3)
	# 		subscription.backends.add(backend4)
	#
	# 		user1 = BasicUser(first_name="ali",
	# 		                  last_name="jahangiri",
	# 		                  username="alijhnm",
	# 		                  email="ajahanmm@gmail.com",
	# 		                  telegram_chat_id="392532307")
	# 		user1.save()
	#
	# 		user2 = BasicUser(first_name="hadi",
	# 		                  last_name="azad del",
	# 		                  email="alijahangiri.m@gmail.com",
	# 		                  username="hazdl")
	# 		user2.save()
	#
	# 		user3 = BasicUser(first_name="siroos",
	# 		                  last_name="shadabfar",
	# 		                  username="shadab")
	# 		user3.save()
	#
	# 		subscription.receiver_users.add(user1)
	# 		subscription.receiver_users.add(user2)
	# 		subscription.receiver_users.add(user3)
	#
	# 		test_model1.extra_field = "new_extra"
	# 		test_model1.save()
	#
	# 		test_model2.extra_field = "new_extra_2"
	# 		test_model2.save()
	#
	# 		# Wait for telegram api to send the message.
	# 		print("Start wait time for telegram messages...")
	# 		telegram_sleep_time = 20
	# 		time.sleep(telegram_sleep_time)
	#
	# 		print("Time's up for sending telegram_messages")
	# 		self.assertTrue(self.telegram_signal_was_called)
	# 		self.assertTrue(self.telegram_response)
	#
	# 		# Wait fro sSMTP server to send the mail
	# 		print("Start wait time for SMTP server emails...")
	# 		email_sleep_time = 10
	# 		time.sleep(email_sleep_time)
	# 		print("Time's up for sending SMTP emails")
	#
	# 		self.assertTrue(self.smtp_signal_was_called)
	# 		self.assertTrue(self.smtp_response)
	#
	# 		print("END of test_register_trigger_templates")




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
