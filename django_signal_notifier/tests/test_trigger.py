import datetime
import time

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals

from django_signal_notifier.messengers import Messengers_name
from django_signal_notifier.models import *
from django_signal_notifier.tests.test_basic import SignalNotifierTestBase
from django.dispatch import Signal
from django_signal_notifier.signals import TelegramMessageSignal, SMTPEmailSignal
from django_signal_notifier.messengers import TelegramBotMessenger, SMTPEmailMessenger

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

        self.telegram_signal_was_called = False
        self.telegram_response = None

        self.smtp_signal_was_called = False
        self.smtp_response = False

        def telegram_message_handler(sender, response_is_ok, **kwargs):
            """
            this functions handles sent telegram messages. when a telegram message is sent,
             a signal(TelegramMessegeSignal) is sent. this function receives the signal and updates test status.
             test status is checked via assertions below.
            :param sender: sender class of the signal. In this case, the sender is TelegramBotMessenger.
            :param response_is_ok: if the message is delivered this param is True.
            :param kwargs: ...
            :return:
            """
            self.telegram_signal_was_called = True
            self.telegram_response = response_is_ok

        TelegramMessageSignal.connect(telegram_message_handler, sender=TelegramBotMessenger)

        def smtp_email_handler(sender, response_is_ok, **kwargs):
            """
            this function handles sent smtp emails. when an email is successfully sent a signal is sent from
             SMTPEmailMessenger. this function handles te signal and updates test status accordingly.
            :param sender: sender class of the signal. In this case it is SMTPEmailMessenger.
            :param response_is_ok: the response provided by the signal sender class
            :param kwargs: ...
            :return:
            """
            self.smtp_signal_was_called = True
            self.smtp_response = response_is_ok

        SMTPEmailSignal.connect(smtp_email_handler, sender=SMTPEmailMessenger)

        test_model1 = TestModel.objects.create(name="new_test_model_1", extra_field="extra")
        test_model2 = TestModel.objects.create(name="new_test_model_2", extra_field="extra2")

        trigger = Trigger.register_trigger(
            verb_name="pre_save",
            action_object=test_model1,
        )

        backend2 = Backend.objects.create(name="TelegramBotMessenger")
        backend3 = Backend.objects.create(name="SMTPEmailMessenger")

        subscription = Subscription.objects.create(trigger=trigger)
        subscription.backends.add(backend2)
        subscription.backends.add(backend3)

        test_model1.extra_field = "new_extra"
        test_model1.save()

        test_model2.extra_field = "new_extra_2"
        test_model2.save()

        # Wait for telegram api to send the message.
        telegram_sleep_time = 5
        time.sleep(telegram_sleep_time)

        self.assertTrue(self.telegram_response)
        self.assertTrue(self.telegram_signal_was_called)

        # Wait fro sSMTP server to send the mail
        email_sleep_time = 10
        time.sleep(email_sleep_time)

        self.assertTrue(self.smtp_signal_was_called)
        self.assertTrue(self.smtp_response)

        print("END of test_register_trigger1")

    def test_register_trigger_user_subscribers(self):
        """
        this test method checks trigger when messages are automatically sent based on subscribers telegram chat id or
        email address.

        :return:
        """
        print("BEGINNING of test_register_trigger_user_subscribers")
        print("verb_name: 'pre_save'", "action_object: instance of testmodel", sep="\n")

        self.telegram_signal_was_called = False
        self.telegram_response = None

        self.smtp_signal_was_called = False
        self.smtp_response = False

        def telegram_message_handler(sender, response_is_ok, **kwargs):
            """
            this functions handles sent telegram messages. when a telegram message is sent,
             a signal(TelegramMessegeSignal) is sent. this function receives the signal and updates test status.
             test status is checked via assertions below.
            :param sender: sender class of the signal. In this case, the sender is TelegramBotMessenger.
            :param response_is_ok: if the message is delivered this param is True.
            :param kwargs: ...
            :return:
            """
            self.telegram_signal_was_called = True
            self.telegram_response = response_is_ok

        TelegramMessageSignal.connect(telegram_message_handler, sender=TelegramBotMessenger)

        def smtp_email_handler(sender, response_is_ok, **kwargs):
            """
            this function handles sent smtp emails. when an email is successfully sent a signal is sent from
             SMTPEmailMessenger. this function handles te signal and updates test status accordingly.
            :param sender: sender class of the signal. In this case it is SMTPEmailMessenger.
            :param response_is_ok: the response provided by the signal sender class
            :param kwargs: ...
            :return:
            """
            self.smtp_signal_was_called = True
            self.smtp_response = response_is_ok

        SMTPEmailSignal.connect(smtp_email_handler, sender=SMTPEmailMessenger)

        test_model1 = TestModel.objects.create(name="new_test_model_1", extra_field="extra")
        test_model2 = TestModel.objects.create(name="new_test_model_2", extra_field="extra2")

        trigger = Trigger.register_trigger(
            verb_name="pre_save",
            action_object=test_model1,
        )
        backend1 = Backend.objects.create(name="BaseMessenger")
        backend2 = Backend.objects.create(name="TelegramBotMessenger")
        backend3 = Backend.objects.create(name="SMTPEmailMessenger")

        subscription = Subscription.objects.create(trigger=trigger)
        subscription.backends.add(backend1)
        subscription.backends.add(backend2)
        subscription.backends.add(backend3)

        user1 = BasicUser(first_name="ali",
                          last_name="jahangiri",
                          username="alijhnm",
                          email="ajahanmm@gmail.com",
                          telegram_chat_id="392532307")
        user1.save()

        user2 = BasicUser(first_name="hadi",
                          last_name="azad del",
                          email="alijahangiri.m@gmail.com",
                          username="hazdl")
        user2.save()

        user3 = BasicUser(first_name="siroos",
                          last_name="shadabfar",
                          username="shadab")
        user3.save()

        subscription.receiver_users.add(user1)
        subscription.receiver_users.add(user2)
        subscription.receiver_users.add(user3)

        test_model1.extra_field = "new_extra"
        test_model1.save()

        test_model2.extra_field = "new_extra_2"
        test_model2.save()

        # Wait for telegram api to send the message.
        # print("Start wait time for telegram messages...")
        # telegram_sleep_time = 20
        # time.sleep(telegram_sleep_time)
        #
        # print("Time's up for sending telegram_messages")
        # self.assertTrue(self.telegram_response)
        # self.assertTrue(self.telegram_signal_was_called)

        # Wait fro sSMTP server to send the mail
        print("Start wait time for SMTP server emails...")
        email_sleep_time = 10
        time.sleep(email_sleep_time)
        print("Time's up for sending SMTP emails")

        self.assertTrue(self.smtp_signal_was_called)
        self.assertTrue(self.smtp_response)

    def test_register_trigger_templates(self):
        """
        this test method checks sent messages when a template is provided via Template model.
        :return:
        """
        print("BEGINNING of test_register_trigger_templates")
        print("verb_name: 'pre_save'", "action_object: instance of testmodel", sep="\n")

        self.telegram_signal_was_called = False
        self.telegram_response = None

        self.smtp_signal_was_called = False
        self.smtp_response = False

        def telegram_message_handler(sender, response_is_ok, **kwargs):
            """
            this functions handles sent telegram messages. when a telegram message is sent,
             a signal(TelegramMessegeSignal) is sent. this function receives the signal and updates test status.
             test status is checked via assertions below.
            :param sender: sender class of the signal. In this case, the sender is TelegramBotMessenger.
            :param response_is_ok: if the message is delivered this param is True.
            :param kwargs: ...
            :return:
            """
            self.telegram_signal_was_called = True
            self.telegram_response = response_is_ok

        TelegramMessageSignal.connect(telegram_message_handler, sender=TelegramBotMessenger)

        def smtp_email_handler(sender, response_is_ok, **kwargs):
            """
            this function handles sent smtp emails. when an email is successfully sent a signal is sent from
             SMTPEmailMessenger. this function handles te signal and updates test status accordingly.
            :param sender: sender class of the signal. In this case it is SMTPEmailMessenger.
            :param response_is_ok: the response provided by the signal sender class
            :param kwargs: ...
            :return:
            """
            self.smtp_signal_was_called = True
            self.smtp_response = response_is_ok

        SMTPEmailSignal.connect(smtp_email_handler, sender=SMTPEmailMessenger)

        test_model1 = TestModel.objects.create(name="new_test_model_1", extra_field="extra")
        test_model2 = TestModel.objects.create(name="new_test_model_2", extra_field="extra2")

        trigger = Trigger.register_trigger(
            verb_name="pre_save",
            action_object=test_model1,
        )

        email_text = "{verb_name} {object_name} {current_time}"
        email_context = dict(verb_name=trigger.verb,
                             object_name="test_model1",
                             current_time=str(datetime.datetime.now().date()))
        email_context = json.dumps(email_context)
        email_template = Template.objects.create(text=email_text, context=email_context)
        # This is an telegram message template which has 4 context_variables
        telegram_text_1 = "{backend_name} {verb_name} {object_name} {current_time}"
        telegram_context_1 = dict(verb_name=trigger.verb,
                                  object_name="test_model1",
                                  current_time=str(datetime.datetime.now()),
                                  backend_name="backend3")
        telegram_context_1 = json.dumps(telegram_context_1)
        telegram_template_1 = Template.objects.create(text=telegram_text_1, context=telegram_context_1)

        telegram_text_2 = "This is another telegram message template which has no context variables."
        telegram_context_2 = json.dumps(dict())
        telegram_template_2 = Template.objects.create(text=telegram_text_2, context=telegram_context_2)

        base_text = "This is a template for base messenger."
        base_context = json.dumps(dict())
        base_template = Template.objects.create(text=base_text, context=base_context)
        backend1 = Backend.objects.create(name="BaseMessenger", template=base_template)
        backend2 = Backend.objects.create(name="TelegramBotMessenger", template=telegram_template_1)
        backend3 = Backend.objects.create(name="SMTPEmailMessenger", template=email_template)
        backend4 = Backend.objects.create(name="TelegramBotMessenger", template=telegram_template_2)

        subscription = Subscription.objects.create(trigger=trigger)
        subscription.backends.add(backend1)
        subscription.backends.add(backend2)
        subscription.backends.add(backend3)
        subscription.backends.add(backend4)

        user1 = BasicUser(first_name="ali",
                          last_name="jahangiri",
                          username="alijhnm",
                          email="ajahanmm@gmail.com",
                          telegram_chat_id="392532307")
        user1.save()

        user2 = BasicUser(first_name="hadi",
                          last_name="azad del",
                          email="alijahangiri.m@gmail.com",
                          username="hazdl")
        user2.save()

        user3 = BasicUser(first_name="siroos",
                          last_name="shadabfar",
                          username="shadab")
        user3.save()

        subscription.receiver_users.add(user1)
        subscription.receiver_users.add(user2)
        subscription.receiver_users.add(user3)

        test_model1.extra_field = "new_extra"
        test_model1.save()

        test_model2.extra_field = "new_extra_2"
        test_model2.save()

        # Wait for telegram api to send the message.
        print("Start wait time for telegram messages...")
        telegram_sleep_time = 20
        time.sleep(telegram_sleep_time)

        print("Time's up for sending telegram_messages")
        self.assertTrue(self.telegram_signal_was_called)
        self.assertTrue(self.telegram_response)

        # Wait fro sSMTP server to send the mail
        print("Start wait time for SMTP server emails...")
        email_sleep_time = 10
        time.sleep(email_sleep_time)
        print("Time's up for sending SMTP emails")

        self.assertTrue(self.smtp_signal_was_called)
        self.assertTrue(self.smtp_response)

        print("END of test_register_trigger_templates")

    def test_register_trigger_by_custom_signal(self):
        print("BEGINNING of test_register_trigger_by_custom_signal")
        # Create custom signal
        custom_signal = Signal(providing_args=["actor"])

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
