from django.contrib.contenttypes.models import ContentType
from django.db.models import signals

from django_signal_notifier.messengers import Messengers_name
from django_signal_notifier.models import Trigger, TestModel, Backend
from django_signal_notifier.tests.test_basic import SignalNotifierTestBase
import django.dispatch

# signals.pre_save = signals.ModelSignal(providing_args=["instance", "raw", "using", "update_fields"],
#                        				 use_caching=True)


class TriggerTestCase(SignalNotifierTestBase):

	def test_register_trigger_by_saved_configs(self):  # check by saved db(fixtures)
		print("BEGINNING of test_register_trigger_by_saved_configs  ")
		TestModel.objects.create(name="new_test_model1", extra_field="extra")
		self.assertEqual(1, 1)  # Todo: Create a test backend that change db, so check its result or effect here
		print("END of test_register_trigger_by_saved_configs")

	def test_register_trigger1(self):
		print("BEGINNING of test_register_trigger1")
		# print(TestModel.objects.all())
		# print(self.testModel1)
		Trigger.register_trigger(
			verb_name="pre_save",
			action_object=TestModel,
		)

		TestModel.objects.create(name="new_test_model", extra_field="extra")

		self.assertEqual(1, 1)
		print("END of test_register_trigger1")

	def test_register_trigger_by_custom_signal(self):
		print("BEGINNING of test_register_trigger_by_custom_signal")
		# Create custom signal
		custom_signal = django.dispatch.Signal(providing_args=["actor"])

		# Add signal to verbs
		Trigger.add_verb_signal("custom_signal", custom_signal)

		# Register new trigger
		trigger = Trigger.register_trigger(
			verb_name="custom_signal",
			action_object=TestModel,
		)

		# Create a backend
		simple_backend = Backend.objects.filter(name=Messengers_name[0][0])[0]

		# Add that backend to trigger's subscription
		trigger.subscription.backends.add(simple_backend)

		# Start test:
		# Sending signal, you should see the simple_backend related output
		custom_signal.send(sender=TestModel, actor=self.user1)  # Must print simple_backend output
		custom_signal.send(sender=TestModel, actor=self.user2)  # Must print nothing!

		self.assertEqual(1, 1)  # Todo: Create a test backend that change db, so check its result or effect here

		print("END of test_register_trigger_by_custom_signal")

	# def test_register_trigger2(self):
	#
	# 	print(self.testModel1)
	# 	Trigger.register_trigger(
	# 		verb_name = "pre_save",
	# 		action_object = TestModel,
	# 		actor = self.user1,
	# 		target = "test_register_trigger2",
	# 	)
	#
	# 	Trigger.register_trigger(
	# 		verb_name="post_delete",
	# 		action_object=TestModel,
	# 		actor=self.user1,
	# 		target="test_register_trigger2",
	# 	)
	#
	# 	TestModel.objects.create(name="new_test_model", extra_field="extra")
	# 	#Todo: Check real values(output)
	#
	# 	self.assertEqual(1, 1)


# class BackendTriggerTestCase(SignalNotifierTestBase):
# 	def test_register_trigger1(self):
# 		print(self.testModel1)
# 		Trigger.register_trigger(
# 			verb_name="pre_save",
# 			action_object=TestModel,
# 			actor=self.user1,
# 			target="test_register_trigger1",
# 		)
#
# 		TestModel.objects.create(name="new_test_model", extra_field="extra")
#
# 		self.assertEqual(1, 1)
