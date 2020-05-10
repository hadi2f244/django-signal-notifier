from django_signal_notifier.models import *
from django_signal_notifier.signals import csignal
from django_signal_notifier.tests.test_init import SignalNotifierTestBase


class TriggerTestCase(SignalNotifierTestBase):

    def test_validate_subscription(self):
        """
        Test subscription validation function
        """
        ###########################################
        # 1. Init:
        ##################
        # 1.1: Create sample backends

        # The template required 'parameter1' as a requirement signal argument
        backend1 = Backend.objects.create(messenger="SimplePrintMessengerTemplateBased",
                                          message_template="SimplePrintMessageTemplateRequiredSignalArgs")

        # The template doesn't requires any signal argument
        backend2 = Backend.objects.create(messenger="SimplePrintMessengerTemplateBased",
                                          message_template="SimplePrintMessageTemplate")

        # The template required 'another_parameter1' as a requirement signal argument
        backend3 = Backend.objects.create(messenger="SimplePrintMessengerTemplateBased",
                                          message_template="AnotherSimplePrintMessageTemplateRequiredSignalArgs")

        ##################
        # 1.2: Register a triggers
        trigger_csignal = Trigger.save_by_model(
            verb_name="csignal"  # Send 'parameter1' as the signal requirement argument
        )
        ##################
        # 1.3.1: Create a subscription for the compatible backends: Both of backends are compatible with the trigger
        subscription_csignal1 = Subscription.objects.create(trigger=trigger_csignal)
        subscription_csignal1.backends.add(backend1)
        subscription_csignal1.receiver_users.add(self.user1)

        subscription_csignal2 = Subscription.objects.create(trigger=trigger_csignal)
        subscription_csignal2.backends.add(backend2)
        subscription_csignal2.receiver_users.add(self.user1)

        # 1.3.2: Create a subscription for the incompatible backend
        subscription_csignal3 = Subscription.objects.create(trigger=trigger_csignal)
        subscription_csignal3.backends.add(backend3)
        subscription_csignal3.receiver_users.add(self.user1)
        ###########################################
        # 2. Test:
        ##################

        # check compatibility for backend1
        try:
            Subscription.validate_subscription(subscription_csignal1,
                                               trigger_csignal,
                                               [backend1])
        except MessageTemplateAndTriggerConflict as e:
            raise(e)

        # check compatibility for backend2
        try:
            Subscription.validate_subscription(subscription_csignal2,
                                               trigger_csignal,
                                               [backend2])
        except MessageTemplateAndTriggerConflict as e:
            raise(e)

        # check compatibility for backend3
        try:
            Subscription.validate_subscription(subscription_csignal3,
                                               trigger_csignal,
                                               [backend3])
            raise(Exception("Incompatible signal must not to work! Check 'Subscription.validate_subscription' function"))
        except MessageTemplateAndTriggerConflict as e:
            print("You must see the subscription validation error, So it works correctly!")