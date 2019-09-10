from django import apps

from django_signal_notifier.models import *
from django_signal_notifier.tests.test_basic import SignalNotifierTestBase


class TriggerTestCase(SignalNotifierTestBase):


	def test_trigger_preSave_simpleMessenger_TestModel(self):
		'''
		This function test register a trigger by pre_save as verb(signal) and TestModel1 as action_object(sender)
		Then calling SimplePrintMessenger send function is test by creating a TestModel1(It called pre_save signal implicitly)

		Test Goals:
			1. SimplePrintMessenger as backend
			2. register_trigger function
			3. Subscription simple functionality
		'''


		# 1. Init:
			# 1.1: Create SimplePrintMessenger backend
		simplePrintMessengerBackend = Backend.objects.create(messenger="SimplePrintMessenger", message_template="BaseMessageTemplate")

			# 1.2: Register a trigger by pre_save as verb(signal) and TestModel1 as action_object(sender)
		trigger_preSave_TestModel = Trigger.register_trigger(
			verb_name="pre_save",
			action_object=TestModel1,
		)

			# 1.3: Create a subscription
		subscription_preSave_TestModel = Subscription.objects.create(trigger=trigger_preSave_TestModel)
		subscription_preSave_TestModel.backends.add(simplePrintMessengerBackend)

		# 2. Test:
			# 2.1: Must call on TestModel1 pre_save
		self.init_simple_messenger_check_signal()
		TestModel1.objects.create(name="new_test_model1", extra_field="extra")

		self.assertTrue(self.simple_messenger_signal_was_called)
		self.assertTrue(self.simple_messenger_response)
		self.assertEqual(self.simple_messenger_context['action_object_content_type'],ContentType.objects.get_for_model(TestModel1))
		self.assertEqual(self.simple_messenger_context['verb'],'pre_save')

			# 2.2: Must not call on TestModel2 pre_save
		self.init_simple_messenger_check_signal()
		TestModel2.objects.create(name="new_test_model1", extra_field="extra")
		self.assertFalse(self.simple_messenger_signal_was_called)
		self.assertIsNone(self.simple_messenger_response)

	def test_trigger_preDelete_simpleMessenger_TestModel_instance(self):
		'''
		This function test register a trigger by pre_save as verb(signal) and a TestModel1 instance as action_object(sender)
		Then calling SimplePrintMessenger send function is test by deleting the TestModel1 instance(It called pre_delete signal implicitly)

		Test Goals:
			1. Trigger action_object functionality
		'''

		# 1. Init:

			# 1.1: Create SimplePrintMessenger backend
		simplePrintMessengerBackend = Backend.objects.create(messenger="SimplePrintMessenger", message_template="BaseMessageTemplate")
		TestModel1_instance = TestModel1.objects.create(name="new_test_model1", extra_field="extra")

			# 1.2: Register a trigger by pre_delete as verb(signal) and TestModel1 as action_object(sender)
		trigger_preDelete_TestModel = Trigger.register_trigger(
			verb_name="pre_delete",
			action_object=TestModel1_instance,
		)

			# 1.3: Create a subscription
		subscription_preSave_TestModel = Subscription.objects.create(trigger=trigger_preDelete_TestModel)
		subscription_preSave_TestModel.backends.add(simplePrintMessengerBackend)


		# 2. Test:
			# 2.1: Must not call on TestModel1_another_instance pre_delete
		self.init_simple_messenger_check_signal()
		TestModel1_another_instance = TestModel1.objects.create(name="new_test_model1", extra_field="extra")
		TestModel1_another_instance.delete()
		self.assertFalse(self.simple_messenger_signal_was_called)
		self.assertIsNone(self.simple_messenger_response)

			# 2.2: Must call on TestModel1_instance pre_delete
		self.init_simple_messenger_check_signal()
		TestModel1_instance_pk = TestModel1_instance.pk
		TestModel1_instance.delete()
		self.assertTrue(self.simple_messenger_signal_was_called)
		self.assertTrue(self.simple_messenger_response)
		self.assertEqual(self.simple_messenger_context['action_object_content_type'],ContentType.objects.get_for_model(TestModel1))
		self.assertEqual(self.simple_messenger_context['verb'],'pre_delete')
		self.assertEqual(self.simple_messenger_context['action_object'].pk, TestModel1_instance_pk)




	# def test_register_trigger_action_object_class(self):
	# 	"""
	# 	this test methods tests trigger when action_object is a CLASS
	# 	:return: this test sends 2 messages because trigger is bound with TestModel1 class and activates for both
	# 			 test_model1 and test_model2
	# 	"""
	# 	print("BEGINNING of test_register_trigger1")
	# 	print("verb_name: 'pre_save'", "action_object: TestModel1", sep="\n")
	# 	# print(TestModel1.objects.all())
	# 	# print(self.testModel1)
	# 	Trigger.register_trigger(
	# 		verb_name="pre_save",
	# 		action_object=TestModel1,
	# 	)
	#
	# 	backend1 = Backend.objects.create(messenger="SMTPEmailMessenger")
	# 	backend2 = Backend.objects.create(messenger="TelegramBotMessenger")
	# 	backend3 = Backend.objects.create(messenger="SimplePrintMessenger")
	#
	# 	subscription = Subscription.objects.first()
	# 	subscription.backends.add(backend1)
	# 	subscription.backends.add(backend2)
	# 	subscription.backends.add(backend3)
	#
	# 	# This 2 will activate the trigger and 2 messages will be sent.
	# 	TestModel1.objects.create(name="new_test_model_1", extra_field="extra")
	# 	TestModel1.objects.create(name="new_test_model_2", extra_field="extra2")
	#
	# 	# This line will not activate the trigger because the trigger is bound with TestModel1 class (and Not TestModel2)
	# 	TestModel2.objects.create(name="test_model2_instance", extra_field="extra")
	#
	# 	self.assertEqual(1, 1)  # Todo: should receive signals when a backend sends a message.
	#
	# 	print("END of test_register_trigger1")

	# def test_register_trigger_action_object_instance(self):
	# 	"""
	# 	this test method tests trigger when action_object is an INSTANCE
	# 	:return: this test sends 1 message because trigger is bound with test_model1 and NOT TestModel1 class itself.
	# 	"""
	#
	# 	print("BEGINNING of test_register_trigger2")
	# 	print("verb_name: 'pre_save'", "action_object: instance of testmodel", sep="\n")
	# 	# print(TestModel1.objects.all())
	# 	# print(self.testModel1)
	#
	#
	#
	# 	test_model1 = TestModel1.objects.create(name="new_test_model_1", extra_field="extra")
	# 	test_model2 = TestModel1.objects.create(name="new_test_model_2", extra_field="extra2")
	#
	# 	trigger = Trigger.register_trigger(
	# 		verb_name="pre_save",
	# 		action_object=test_model1,
	# 	)
	#
	# 	backend2 = Backend.objects.create(messenger="TelegramBotMessenger")
	# 	backend3 = Backend.objects.create(messenger="SMTPEmailMessenger")
	#
	# 	subscription = Subscription.objects.create(trigger=trigger)
	# 	subscription.backends.add(backend2)
	# 	subscription.backends.add(backend3)
	#
	# 	test_model1.extra_field = "new_extra"
	# 	test_model1.save()
	#
	# 	test_model2.extra_field = "new_extra_2"
	# 	test_model2.save()
	#
	# 	# Wait for telegram api to send the message.
	# 	telegram_sleep_time = 5
	# 	time.sleep(telegram_sleep_time)
	#
	# 	self.assertTrue(self.telegram_response)
	# 	self.assertTrue(self.telegram_signal_was_called)
	#
	# 	# Wait fro sSMTP server to send the mail
	# 	email_sleep_time = 10
	# 	time.sleep(email_sleep_time)
	#
	# 	self.assertTrue(self.smtp_signal_was_called)
	# 	self.assertTrue(self.smtp_response)
	#
	# 	print("END of test_register_trigger1")

	def test_register_trigger_user_subscribers(self):
		'''
			This function test register a trigger by pre_save as verb(signal) and TestModel1 as action_object(sender)
			Then calling SimplePrintMessenger send function is test by creating a TestModel1(It called pre_save signal implicitly)

			Test Goals:
				1. SimplePrintMessenger as backend
				2. register_trigger function
				3. Subscription simple functionality
			'''

		# Todo: There exists a problem on Content_Type ("ContentType matching query does not exist.")
		# I searched and do sum solutions but they haven't worked(some django update make solution harder!)
		# https://stackoverflow.com/questions/29550102/importerror-cannot-import-name-update-all-contenttypes/29550255#29550255
		# https://stackoverflow.com/questions/11672976/contenttype-matching-query-does-not-exist-on-post-syncdb/17614700#17614700
		# 
		# # from django.apps import apps
		# # from django.contrib.contenttypes.management import create_contenttypes
		# # def update_all_contenttypes(**kwargs):
		# # 	for app_config in apps.get_app_configs():
		# # 		create_contenttypes(app_config, **kwargs)
		# # update_all_contenttypes()



		# 1. Init:
		# 1.1: Create SimplePrintMessenger backend
		simplePrintMessengerBackend = Backend.objects.create(messenger="SimplePrintMessenger", message_template="BaseMessageTemplate")

		# 1.2: Register a trigger by pre_save as verb(signal) and TestModel1 as action_object(sender)
		trigger_preSave_TestModel = Trigger.register_trigger(
			verb_name="pre_save",
			action_object=TestModel2,
		)

		# 1.3: Create a subscription and add a user to its subscribers
		subscription_preSave_TestModel = Subscription.objects.create(trigger=trigger_preSave_TestModel)
		subscription_preSave_TestModel.backends.add(simplePrintMessengerBackend)
		subscription_preSave_TestModel.receiver_users.add(self.user1)

		# 2. Test:
		# 2.1: Must call on TestModel1 pre_save
		self.init_simple_messenger_check_signal()
		TestModel2.objects.create(name="new_test_model2", extra_field="extra")

		self.assertTrue(self.simple_messenger_signal_was_called)
		self.assertTrue(self.simple_messenger_response)
		self.assertEqual(list(self.simple_messenger_users), [self.user1])


	# 	def test_register_trigger_user_subscribers(self):
# 		"""
# 		this test method checks trigger when messages are automatically sent based on subscribers telegram chat id or
# 		email address.
#
# 		:return:
# 		"""
# 		print("BEGINNING of test_register_trigger_user_subscribers")
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
# 		backend1 = Backend.objects.create(messenger="BaseMessenger")
# 		backend2 = Backend.objects.create(messenger="TelegramBotMessenger")
# 		backend3 = Backend.objects.create(messenger="SMTPEmailMessenger")
#
# 		subscription = Subscription.objects.create(trigger=trigger)
# 		subscription.backends.add(backend1)
# 		subscription.backends.add(backend2)
# 		subscription.backends.add(backend3)
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
# 		# print("Start wait time for telegram messages...")
# 		# telegram_sleep_time = 20
# 		# time.sleep(telegram_sleep_time)
# 		#
# 		# print("Time's up for sending telegram_messages")
# 		# self.assertTrue(self.telegram_response)
# 		# self.assertTrue(self.telegram_signal_was_called)
#
# 		# Wait fro sSMTP server to send the mail
# 		print("Start wait time for SMTP server emails...")
# 		email_sleep_time = 10
# 		time.sleep(email_sleep_time)
# 		print("Time's up for sending SMTP emails")
#
# 		self.assertTrue(self.smtp_signal_was_called)
# 		self.assertTrue(self.smtp_response)

	def test_template(self):
		pass
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
#
	def test_register_trigger_by_custom_signal(self):
		pass
# 	def test_register_trigger_by_custom_signal(self):
# 		print("BEGINNING of test_register_trigger_by_custom_signal")
# 		# Create custom signal
# 		custom_signal = Signal(providing_args=["actor"])
#
# 		# Add signal to verbs
# 		Trigger.add_verb_signal("custom_signal", custom_signal)
#
# 		# Register new trigger
# 		trigger = Trigger.register_trigger(
# 			verb_name="custom_signal",
# 			action_object=TestModel1,
# 		)
#
# 		# Create a backend
# 		simple_backend = Backend.objects.filter(messenger=messenger_names[0][0])[0]
#
# 		# Add that backend to trigger's subscription
# 		trigger.subscription.backends.add(simple_backend)
#
# 		# Start test:
# 		# Sending signal, you should see the simple_backend related output
# 		custom_signal.send(sender=TestModel1, actor=self.user1)  # Must print simple_backend output
# 		custom_signal.send(sender=TestModel1, actor=self.user2)  # Must print nothing!
#
# 		self.assertEqual(1, 1)  # Todo: Create a test backend that change db, so check its result or effect here
#
# 		print("END of test_register_trigger_by_custom_signal")
#
