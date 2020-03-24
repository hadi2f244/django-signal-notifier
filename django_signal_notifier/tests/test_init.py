from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.test import TransactionTestCase
from django_signal_notifier import settings as app_settings

from django_signal_notifier.messengers import SimplePrintMessenger, \
    SimplePrintMessengerTemplateBased, AnotherSimplePrintMessenger
from django_signal_notifier.models import TestModel1, Trigger, Backend, Subscription, TestModel2
from django.apps import apps
from django_signal_notifier.signals import SimplePrintMessengerSignal, \
    SimplePrintMessengerSignalTemplateBased, AnotherSimplePrintMessengerSignal

User = get_user_model()


class SignalNotifierTestBase(TransactionTestCase):

    def init_simple_messenger_check_signal(self):
        '''
        reinitialize simple messenger handler results.
        :return:
        '''
        self.simple_messenger_signal_was_called = False
        self.simple_messenger_responses = None
        self.simple_messenger_sender = None
        self.simple_messenger_users = None
        self.simple_messenger_trigger_context = None
        self.simple_messenger_signal_kwargs = None

        def simple_messenger_message_handler(sender, responses, users, trigger_context, signal_kwargs, **kwargs):
            """
            this functions handles sent telegram messages. when a telegram message is sent,
             a signal(TelegramMessegeSignal) is sent. this function receives the signal and updates test status.
             test status is checked via assertions below.
            :param sender: sender class of the signal. In this case, the sender is TelegramBotMessenger.
            :param response: if the message is delivered this param is True.
            :param kwargs: ...
            :return:
            """
            self.simple_messenger_signal_was_called = True
            self.simple_messenger_responses = responses
            self.simple_messenger_sender = sender
            self.simple_messenger_users = users
            self.simple_messenger_trigger_context = trigger_context
            self.simple_messenger_signal_kwargs = signal_kwargs

        self.simple_messenger_message_handler = simple_messenger_message_handler

        # Disconnecting to avoid extra calling
        SimplePrintMessengerSignal.disconnect(self.simple_messenger_message_handler, sender=SimplePrintMessenger)
        SimplePrintMessengerSignal.connect(self.simple_messenger_message_handler, sender=SimplePrintMessenger)
        SimplePrintMessengerSignalTemplateBased.disconnect(self.simple_messenger_message_handler,
                                                           sender=SimplePrintMessengerTemplateBased)
        SimplePrintMessengerSignalTemplateBased.connect(self.simple_messenger_message_handler,
                                                        sender=SimplePrintMessengerTemplateBased)

    def init_another_simple_messenger_check_signal(self):
        '''
        reinitialize another simple messenger handler results.
        :return:
        '''
        self.another_simple_messenger_signal_was_called = False
        self.another_simple_messenger_responses = None
        self.another_simple_messenger_sender = None
        self.another_simple_messenger_users = None
        self.another_simple_messenger_trigger_context = None
        self.another_simple_messenger_signal_kwargs = None

        def another_simple_messenger_message_handler(sender, responses, users, trigger_context, signal_kwargs,
                                                     **kwargs):
            """
            this functions handles sent telegram messages. when a telegram message is sent,
             a signal(TelegramMessegeSignal) is sent. this function receives the signal and updates test status.
             test status is checked via assertions below.
            :param sender: sender class of the signal. In this case, the sender is TelegramBotMessenger.
            :param response: if the message is delivered this param is True.
            :param kwargs: ...
            :return:
            """
            self.another_simple_messenger_signal_was_called = True
            self.another_simple_messenger_responses = responses
            self.another_simple_messenger_sender = sender
            self.another_simple_messenger_users = users
            self.another_simple_messenger_trigger_context = trigger_context
            self.another_simple_messenger_signal_kwargs = signal_kwargs

        self.another_simple_messenger_message_handler = another_simple_messenger_message_handler

        # Disconnecting to avoid extra calling
        AnotherSimplePrintMessengerSignal.disconnect(self.another_simple_messenger_message_handler,
                                                     sender=AnotherSimplePrintMessenger)
        AnotherSimplePrintMessengerSignal.connect(self.another_simple_messenger_message_handler,
                                                  sender=AnotherSimplePrintMessenger)

    def setUp(self):
        super(SignalNotifierTestBase, self).setUp()

        # self.UserModel = apps.get_model('django_signal_notifier', 'BasicUser')
        self.UserModel = apps.get_model(app_settings.AUTH_USER_MODEL)

        self.group1 = Group.objects.create(name='group1')
        self.group2 = Group.objects.create(name='group2')

        ProfileModel = apps.get_model(app_settings.PROFILE_MODEL)
        self.user1 = self.UserModel(first_name="hadi",
                                    last_name="azaddel",
                                    email="hadi2f2@gmail.com",
                                    username="hazdl")
        self.user1.save()
        self.profile1 = ProfileModel(user=self.user1,
                                     telegram_chat_id="78067664")
        self.profile1.save()

        self.user2 = self.UserModel.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.user2.save()
        self.profile2 = ProfileModel(user=self.user2)
        self.profile2.save()

        self.user3 = self.UserModel(first_name="hadi1",
                                    last_name="azaddel1",
                                    email="hadi2f21@gmail.com",
                                    username="hazdl1")
        self.user3.save()
        self.profile3 = ProfileModel(user=self.user3,
                                     telegram_chat_id="78067664")
        self.profile3.save()

        self.user1.groups.add(self.group1)
        self.user2.groups.add(self.group2)
        self.user3.groups.add(self.group2)

        self.init_simple_messenger_check_signal()
        self.init_another_simple_messenger_check_signal()

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.user3.delete()
        super(SignalNotifierTestBase, self).tearDown()

    def test_save_trigger_actionObject_class_template(self, signal_name, messenger, message_template):
        """
        This function test register a trigger by pre_save as verb(signal) and TestModel1 as action_object(sender)
        Then calling SimplePrintMessenger send function is test by creating a TestModel1(It called pre_save signal implicitly)

        Test Goals:
            1. SimplePrintMessenger as backend
            2. save_by_model function
            3. Subscription simple functionality
        """

        # A. By pre_save signal

        # 1. Init:
        # 1.1: Create SimplePrintMessenger backend
        simplePrintMessengerBackend = Backend.objects.create(messenger=messenger, message_template=message_template)

        # 1.2: Register a trigger by pre_save as verb(signal) and TestModel1 as action_object(sender)
        trigger_preSave_TestModel = Trigger.save_by_model(
            verb_name=signal_name,
            action_object=TestModel1,
        )

        # 1.3: Create a subscription
        subscription_verb_TestModel = Subscription.objects.create(trigger=trigger_preSave_TestModel)
        subscription_verb_TestModel.backends.add(simplePrintMessengerBackend)
        subscription_verb_TestModel.receiver_users.add(self.user1)

        # 2. Test:
        # 2.1: Must call on TestModel1 pre_save
        self.init_simple_messenger_check_signal()
        TestModel1.objects.create(name="new_test_model1", extra_field="extra")

        self.assertTrue(self.simple_messenger_signal_was_called)
        self.assertEqual(self.simple_messenger_trigger_context['action_object_content_type'],
                         ContentType.objects.get_for_model(TestModel1))
        self.assertEqual(self.simple_messenger_trigger_context['verb'], signal_name)

        # 2.2: Must not call on TestModel2 pre_save
        self.init_simple_messenger_check_signal()
        TestModel2.objects.create(name="new_test_model1", extra_field="extra")
        self.assertFalse(self.simple_messenger_signal_was_called)
