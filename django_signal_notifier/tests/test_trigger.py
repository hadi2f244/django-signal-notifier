from django.db.models import signals

from django_signal_notifier.models import Trigger, TestModel
from django_signal_notifier.tests.test_basic import SignalNotifierTestBase

# signals.pre_save = signals.ModelSignal(providing_args=["instance", "raw", "using", "update_fields"],
#                        use_caching=True)

class TriggerTestCase(SignalNotifierTestBase):

	def test_register_trigger_by_saved_configs(self): # check by saved db(fixtures)
		TestModel.objects.create(name="new_test_model1", extra_field="extra")
		self.assertEqual(1, 1) #Todo: Create a test backend that change db, so check its result or effect here

	def test_register_trigger1(self):

		# print(TestModel.objects.all())
		# print(self.testModel1)
		Trigger.register_trigger(
			verb_name = "pre_save",
			action_object = TestModel,
			actor = self.user1,
			target = "test_register_trigger1",
		)

		TestModel.objects.create(name="new_test_model", extra_field="extra")

		self.assertEqual(1, 1)

	def test_register_trigger_by_custom_signal(self): 
		TestModel.objects.create(name="new_test_model1", extra_field="extra")
		self.assertEqual(1, 1) #Todo: Create a test backend that change db, so check its result or effect here


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
