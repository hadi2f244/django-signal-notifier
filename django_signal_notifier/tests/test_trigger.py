from django.db.models import signals

from django_signal_notifier.models import Trigger, TestModel
from django_signal_notifier.tests.test_basic import SignalNotifierTestBase

# signals.pre_save = signals.ModelSignal(providing_args=["instance", "raw", "using", "update_fields"],
#                        use_caching=True)

class TriggerTestCase(SignalNotifierTestBase):
	def test_register_trigger1(self):

		print(self.testModel1)
		Trigger.register_trigger(
			verb_name = "pre_save",
			verb_signal = signals.pre_save,
			action_object = TestModel,
			actor = self.user1,
			target = "test_register_trigger1",
		)

		TestModel.objects.create(name="new_test_model", extra_field="extra")

		self.assertEqual(1, 1)

	def test_register_trigger2(self):

		print(self.testModel1)
		Trigger.register_trigger(
			verb_name = "pre_save",
			verb_signal = signals.pre_save,
			action_object = TestModel,
			actor = self.user1,
			target = "test_register_trigger2",
		)

		Trigger.register_trigger(
			verb_name="post_delete",
			verb_signal=signals.post_delete,
			action_object=TestModel,
			actor=self.user1,
			target="test_register_trigger2",
		)

		TestModel.objects.create(name="new_test_model", extra_field="extra")

		self.assertEqual(1, 1)

		# Now create the same notification again, this should not create new
		# objects in the DB but instead increase the count of that notification!
		# utils.notify("Another test", self.TEST_KEY)

		# self.assertEqual(models.Notification.objects.filter(occurrences=2).count(), 2)