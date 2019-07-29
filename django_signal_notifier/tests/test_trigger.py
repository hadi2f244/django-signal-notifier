from django.contrib.contenttypes.models import ContentType
from django.db.models import signals

from django_signal_notifier.messengers import Messengers_name
from django_signal_notifier.models import Trigger, TestModel, Backend, Subscription, TestModel2
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

    def test_register_trigger_action_object_class(self):
        """
        this test methods tests trigger when action_object is a CLASS
        :return: this test sends 2 messages because trigger is bound with TestModel class and activates for both
                 test_model1 and test_model2
        """
        print("BEGINNING of test_register_trigger1")
        print("verb_name: 'pre_save'", "action_object: TestModel", sep="\n")
        # print(TestModel.objects.all())
        # print(self.testModel1)
        Trigger.register_trigger(
            verb_name="pre_save",
            action_object=TestModel,
        )

        backend1 = Backend.objects.create(name="SMTPEmailMessenger")
        backend2 = Backend.objects.create(name="TelegramBotMessenger")
        backend3 = Backend.objects.create(name="SimplePrintMessenger1")

        subscription = Subscription.objects.first()
        subscription.backends.add(backend1)
        subscription.backends.add(backend2)
        subscription.backends.add(backend3)

        # This 2 will activate the trigger and 2 messages will be sent.
        TestModel.objects.create(name="new_test_model_1", extra_field="extra")
        TestModel.objects.create(name="new_test_model_2", extra_field="extra2")

        # This line will not activate the trigger because the trigger is bound with TestModel class (and Not TestModel2)
        TestModel2.objects.create(name="test_model2_instance", extra_field="extra")

        self.assertEqual(1, 1)  # Todo: should receive signals when a backend sends a message.

        print("END of test_register_trigger1")

    def test_register_trigger_action_object_instance(self):
        """
        this test method tests trigger when action_object is an INSTANCE
        :return: this test sends 1 message because trigger is bound with test_model1 and NOT TestModel class itself.
        """
        print("BEGINNING of test_register_trigger2")
        print("verb_name: 'pre_save'", "action_object: instance of testmodel", sep="\n")
        # print(TestModel.objects.all())
        # print(self.testModel1)

        test_model1 = TestModel.objects.create(name="new_test_model_1", extra_field="extra")
        test_model2 = TestModel.objects.create(name="new_test_model_2", extra_field="extra2")
        
        Trigger.register_trigger(
            verb_name="pre_save",
            action_object=test_model1,
        )

        backend2 = Backend.objects.create(name="TelegramBotMessenger")
        backend3 = Backend.objects.create(name="SimplePrintMessenger1")

        subscription = Subscription.objects.first()
        subscription.backends.add(backend2)
        subscription.backends.add(backend3)

        test_model1.extra_field = "new_extra"
        test_model1.save()

        test_model2.extra_field = "new_extra_2"
        test_model2.save()

        self.assertEqual(1, 1)  # Todo: should receive signals when a backend sends a message.
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
