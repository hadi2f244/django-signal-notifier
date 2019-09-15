from django import apps

from django_signal_notifier.models import *
from django_signal_notifier.tests.test_init import SignalNotifierTestBase


class TriggerTestCase(SignalNotifierTestBase):

	def test_preSave_trigger_actionObject_class(self):
		self.test_save_trigger_actionObject_class_template(signal_name='pre_save', messenger="SimplePrintMessenger", message_template="BaseMessageTemplate")

	def test_preSave_postSave_trigger_actionObject_class(self):
		print("Must run 1 time for pre_save:")
		self.test_save_trigger_actionObject_class_template(signal_name='pre_save', messenger="SimplePrintMessenger", message_template="BaseMessageTemplate")

		print("Must run 2 times first for pre_save, then for post_save:")
		self.test_save_trigger_actionObject_class_template(signal_name='post_save', messenger="SimplePrintMessenger", message_template="BaseMessageTemplate")



	def test_trigger_actionObject_instance(self):
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
		TestModel1_another_instance = TestModel1.objects.create(name="new_test_model2", extra_field="extra")
		TestModel1_another_instance.delete()
		self.assertFalse(self.simple_messenger_signal_was_called)

			# 2.2: Must call on TestModel1_instance pre_delete
		self.init_simple_messenger_check_signal()
		TestModel1_instance_pk = TestModel1_instance.pk
		TestModel1_instance.delete()
		self.assertTrue(self.simple_messenger_signal_was_called)
		self.assertEqual(self.simple_messenger_trigger_context['action_object_content_type'],ContentType.objects.get_for_model(TestModel1))
		self.assertEqual(self.simple_messenger_trigger_context['verb'],'pre_delete')
		self.assertEqual(self.simple_messenger_trigger_context['action_object'].pk, TestModel1_instance_pk)


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
		subscription_preSave_TestModel.receiver_groups.add(self.group2)

		# 2. Test:
		# 2.1: Must call on TestModel1 pre_save
		self.init_simple_messenger_check_signal()
		TestModel2.objects.create(name="new_test_model1", extra_field="extra")

		self.assertTrue(self.simple_messenger_signal_was_called)
		self.assertEqual(list(self.simple_messenger_users), [self.user1, self.user2, self.user3])


#
	def test_register_trigger_by_custom_signal(self):
		pass
# 	def test_register_trigger_by_custom_signal(self):
# 		print("BEGINNING of test_register_trigger_by_custom_signal")
# 		# Create custom signal
# 		custom_signal = Signal(providing_args=["actor_object"])
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
# 		custom_signal.send(sender=TestModel1, actor_object=self.user1)  # Must print simple_backend output
# 		custom_signal.send(sender=TestModel1, actor_object=self.user2)  # Must print nothing!
#
# 		self.assertEqual(1, 1)  # Todo: Create a test backend that change db, so check its result or effect here
#
# 		print("END of test_register_trigger_by_custom_signal")
#
