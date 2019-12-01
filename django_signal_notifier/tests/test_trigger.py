from django_signal_notifier.models import *
from django_signal_notifier.signals import csignal
from django_signal_notifier.tests.test_init import SignalNotifierTestBase


class TriggerTestCase(SignalNotifierTestBase):

    def test_preSave_trigger_actionObject_class(self):
        '''
        Simplest example checking
        '''
        self.test_save_trigger_actionObject_class_template(signal_name='pre_save', messenger="SimplePrintMessenger",
                                                           message_template="BaseMessageTemplate")

    def test_preSave_postSave_trigger_actionObject_class(self):
        print("Must run 1 time for pre_save:")
        self.test_save_trigger_actionObject_class_template(signal_name='pre_save', messenger="SimplePrintMessenger",
                                                           message_template="BaseMessageTemplate")

        print("\nMust run 2 times first for pre_save, then for post_save:")
        self.test_save_trigger_actionObject_class_template(signal_name='post_save', messenger="SimplePrintMessenger",
                                                           message_template="BaseMessageTemplate")

    def test_trigger_actionObject_instance(self):
        '''
        This function test register a trigger by pre_save as verb(signal) and a TestModel1 instance as action_object(sender)
        Then send function of SimplePrintMessenger calling is test by deleting the TestModel1 instance(It called pre_delete signal implicitly)

        Test Goals:
            1. Trigger action_object functionality
        '''
        ###########################################
        # 1. Init:
        ##################
        # 1.1: Create SimplePrintMessenger backend
        simplePrintMessengerBackend = Backend.objects.create(messenger="SimplePrintMessenger",
                                                             message_template="BaseMessageTemplate")
        TestModel1_instance = TestModel1.objects.create(name="new_test_model1", extra_field="extra")
        ##################
        # 1.2: Register a trigger by pre_delete as verb(signal) and TestModel1 as action_object(sender)
        trigger_preDelete_TestModel = Trigger.register_trigger(
            verb_name="pre_delete",
            action_object=TestModel1_instance,
        )
        ##################
        # 1.3: Create a subscription
        subscription_preSave_TestModel = Subscription.objects.create(trigger=trigger_preDelete_TestModel)
        subscription_preSave_TestModel.backends.add(simplePrintMessengerBackend)

        ###########################################
        # 2. Test:
        ##################
        # 2.1: Must not call on TestModel1_another_instance pre_delete
        self.init_simple_messenger_check_signal()
        TestModel1_another_instance = TestModel1.objects.create(name="new_test_model2", extra_field="extra")
        TestModel1_another_instance.delete()
        self.assertFalse(self.simple_messenger_signal_was_called)
        ##################
        # 2.2: Must call on TestModel1_instance pre_delete
        self.init_simple_messenger_check_signal()
        TestModel1_instance_pk = TestModel1_instance.pk
        TestModel1_instance.delete()
        self.assertTrue(self.simple_messenger_signal_was_called)
        self.assertEqual(self.simple_messenger_trigger_context['action_object_content_type'],
                         ContentType.objects.get_for_model(TestModel1))
        self.assertEqual(self.simple_messenger_trigger_context['verb'], 'pre_delete')
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

        ###########################################
        # 1. Init:
        ##################
        # 1.1: Create SimplePrintMessenger backend
        simplePrintMessengerBackend = Backend.objects.create(messenger="SimplePrintMessenger",
                                                             message_template="BaseMessageTemplate")
        ##################
        # 1.2: Register a trigger by pre_save as verb(signal) and TestModel1 as action_object(sender)
        trigger_preSave_TestModel = Trigger.register_trigger(
            verb_name="pre_save",
            action_object=TestModel2,
        )
        ##################
        # 1.3: Create a subscription and add a user to its subscribers
        subscription_preSave_TestModel = Subscription.objects.create(trigger=trigger_preSave_TestModel)
        subscription_preSave_TestModel.backends.add(simplePrintMessengerBackend)
        subscription_preSave_TestModel.receiver_users.add(self.user1)
        subscription_preSave_TestModel.receiver_groups.add(self.group2)

        ###########################################
        # 2. Test:
        ##################
        # 2.1: Must call on TestModel1 pre_save
        self.init_simple_messenger_check_signal()
        TestModel2.objects.create(name="new_test_model1", extra_field="extra")

        self.assertTrue(self.simple_messenger_signal_was_called)
        self.assertEqual(list(self.simple_messenger_users), [self.user1, self.user2, self.user3])

    #
    def test_register_trigger_by_custom_signal(self):
        '''
            This function test registering a custom trigger

            Test Goals:
                1. registering custom trigger
                2. check calling the created trigger's handler
            '''

        ###########################################
        # 1. Init:
        ##################
        # 1.1: Create SimplePrintMessenger backend
        ####
        simplePrintMessengerBackend = Backend.objects.create(messenger="SimplePrintMessenger",
                                                             message_template="BaseMessageTemplate")
        ##################
        # 1.2: Register a trigger by csignal as verb(signal)
        trigger_csignal = Trigger.register_trigger(
            verb_name="csignal"
        )
        ##################
        # 1.3: Create a subscription and add a user to its subscribers
        subscription_csignal = Subscription.objects.create(trigger=trigger_csignal)
        subscription_csignal.backends.add(simplePrintMessengerBackend)
        subscription_csignal.receiver_users.add(self.user1)

        ###########################################
        # 2. Test:
        ##################
        self.init_simple_messenger_check_signal()

        #       take place:
        csignal.send_robust(sender=None, parameter1='test')

        self.assertTrue(self.simple_messenger_signal_was_called)
        self.assertEqual(self.simple_messenger_trigger_context['verb'], 'csignal')

    def test_correlative_csignal_csignalWithActionObj_trigger_class(self):
        '''
             This function is for testing two correlative signals. For example consider these two signals:
                    1. A pure custom signal (just verb)
                    2. Same custom signal with action_object (verb + action_object)


               Test Goals:
                   These two results are expected:
                        1. By calling(sending) the first signal, the trigger which is related to it must be called
                        2. By calling(sending) the second signal, both of triggers that are related to the signals must be called
               '''
        ###########################################
        # 1. Init:
        ##################
        # 1.1: Create SimplePrintMessenger and AnotherSimplePrintMessanger backend
        simplePrintMessengerBackend = Backend.objects.create(messenger="SimplePrintMessenger",
                                                             message_template="BaseMessageTemplate")
        anotherSimplePrintMessengerBackend = Backend.objects.create(messenger="AnotherSimplePrintMessenger",
                                                                    message_template="BaseMessageTemplate")
        ##################
        # 1.2:
        #   Register a trigger by csignal signal as verb(signal)
        #   Register another trigger by csignal as verb(signal) and TestModel1 as action_object(sender)
        trigger_csignal = Trigger.register_trigger(
            verb_name="csignal"
        )
        trigger_csignal_TestModel = Trigger.register_trigger(
            verb_name='csignal',
            action_object=TestModel1,
        )
        ##################
        # 1.3:
        #   Create a subscription for the first trigger
        #   Create a subscription for the second trigger
        subscription_csignal = Subscription.objects.create(trigger=trigger_csignal)
        subscription_csignal.backends.add(simplePrintMessengerBackend)
        subscription_csignal.receiver_users.add(self.user1)

        subscription_csignal_TestModel = Subscription.objects.create(trigger=trigger_csignal_TestModel)
        subscription_csignal_TestModel.backends.add(anotherSimplePrintMessengerBackend)
        subscription_csignal_TestModel.receiver_users.add(self.user1)

        ###########################################
        # 2. Test: Just pay attention to  Take action part
        ##################
        # 2.1: Must just call the first one signal
        self.init_simple_messenger_check_signal()
        self.init_another_simple_messenger_check_signal()

        #       Take action:
        csignal.send_robust(sender=None, parameter1='test')

        #       Check the first one is called
        self.assertTrue(self.simple_messenger_signal_was_called)
        self.assertEqual(self.simple_messenger_trigger_context['verb'], 'csignal')

        #       Check second one isn't called
        self.assertFalse(self.another_simple_messenger_signal_was_called)

        ##################
        # 2.2: Must call both signals
        self.init_simple_messenger_check_signal()
        self.init_another_simple_messenger_check_signal()

        #       Take action:
        csignal.send_robust(sender=TestModel1, parameter1='test')

        #       Check the first one is called
        self.assertTrue(self.simple_messenger_signal_was_called)
        self.assertEqual(self.simple_messenger_trigger_context['verb'], 'csignal')

        #       Check the second one is called
        self.assertTrue(self.another_simple_messenger_signal_was_called)
        self.assertEqual(self.another_simple_messenger_trigger_context['action_object_content_type'],
                         ContentType.objects.get_for_model(TestModel1))
        self.assertEqual(self.another_simple_messenger_trigger_context['verb'], 'csignal')

    def test_correlative_csignal_csignalWithActorObj_trigger_class(self):
        '''
             Like previous function but check actor_object instead of action_object
               '''
        ###########################################
        # 1. Init:
        ##################
        # 1.1: Create SimplePrintMessenger and AnotherSimplePrintMessanger backend
        simplePrintMessengerBackend = Backend.objects.create(messenger="SimplePrintMessenger",
                                                             message_template="BaseMessageTemplate")
        anotherSimplePrintMessengerBackend = Backend.objects.create(messenger="AnotherSimplePrintMessenger",
                                                                    message_template="BaseMessageTemplate")
        ##################
        # 1.2:
        #   Register a trigger by csignal signal as verb(signal)
        #   Register another trigger by csignal as verb(signal) and TestModel1 as actor_object(sender)
        trigger_csignal = Trigger.register_trigger(
            verb_name="csignal"
        )
        trigger_csignal_TestModel = Trigger.register_trigger(
            verb_name='csignal',
            actor_object=TestModel1,
        )
        ##################
        # 1.3:
        #   Create a subscription for the first trigger
        #   Create a subscription for the second trigger
        subscription_csignal = Subscription.objects.create(trigger=trigger_csignal)
        subscription_csignal.backends.add(simplePrintMessengerBackend)
        subscription_csignal.receiver_users.add(self.user1)

        subscription_csignal_TestModel = Subscription.objects.create(trigger=trigger_csignal_TestModel)
        subscription_csignal_TestModel.backends.add(anotherSimplePrintMessengerBackend)
        subscription_csignal_TestModel.receiver_users.add(self.user1)

        ###########################################
        # 2. Test: Just pay attention to  Take action part
        ##################
        # 2.1: Must just call the first one signal
        self.init_simple_messenger_check_signal()
        self.init_another_simple_messenger_check_signal()

        #       Take action:
        csignal.send_robust(sender=None, parameter1='test')

        #       Check the first one is called
        self.assertTrue(self.simple_messenger_signal_was_called)
        self.assertEqual(self.simple_messenger_trigger_context['verb'], 'csignal')

        #       Check second one isn't called
        self.assertFalse(self.another_simple_messenger_signal_was_called)

        ##################
        # 2.2: Must call both signals
        self.init_simple_messenger_check_signal()
        self.init_another_simple_messenger_check_signal()

        #       Take action:
        csignal.send_robust(sender=None, actor_object=TestModel1, parameter1='test')

        #       Check the first one is called
        self.assertTrue(self.simple_messenger_signal_was_called)
        self.assertEqual(self.simple_messenger_trigger_context['verb'], 'csignal')

        #       Check the second one is called
        self.assertTrue(self.another_simple_messenger_signal_was_called)
        self.assertEqual(self.another_simple_messenger_trigger_context['actor_object_content_type'],
                         ContentType.objects.get_for_model(TestModel1))
        self.assertEqual(self.another_simple_messenger_trigger_context['verb'], 'csignal')

    def test_correlative_csignalWithActionObj_csignalWithActionActorObj_trigger_class(self):
        '''
             Like two previous functions but check actor_object and action_object both
               '''
        ###########################################
        # 1. Init:
        ##################
        # 1.1: Create SimplePrintMessenger and AnotherSimplePrintMessanger backend
        simplePrintMessengerBackend = Backend.objects.create(messenger="SimplePrintMessenger",
                                                             message_template="BaseMessageTemplate")
        anotherSimplePrintMessengerBackend = Backend.objects.create(messenger="AnotherSimplePrintMessenger",
                                                                    message_template="BaseMessageTemplate")
        ##################
        # 1.2:
        #   Register a trigger by csignal signal as verb(signal)
        #   Register another trigger by csignal as verb(signal) and TestModel1 as actor_object(sender)
        trigger_csignal = Trigger.register_trigger(
            verb_name="csignal",
            action_object=TestModel1,
        )
        trigger_csignal_TestModel = Trigger.register_trigger(
            verb_name='csignal',
            action_object=TestModel1,
            actor_object=TestModel2,
        )
        ##################
        # 1.3:
        #   Create a subscription for the first trigger
        #   Create a subscription for the second trigger
        subscription_csignal = Subscription.objects.create(trigger=trigger_csignal)
        subscription_csignal.backends.add(simplePrintMessengerBackend)
        subscription_csignal.receiver_users.add(self.user1)

        subscription_csignal_TestModel = Subscription.objects.create(trigger=trigger_csignal_TestModel)
        subscription_csignal_TestModel.backends.add(anotherSimplePrintMessengerBackend)
        subscription_csignal_TestModel.receiver_users.add(self.user1)

        ###########################################
        # 2. Test: Just pay attention to  Take action part
        ##################
        # 2.1: Must not call any of them
        self.init_simple_messenger_check_signal()
        self.init_another_simple_messenger_check_signal()

        #       Take action:
        csignal.send_robust(sender=None, parameter1='test')

        #       Check the first one isn't called
        self.assertFalse(self.simple_messenger_signal_was_called)

        #       Check second one isn't called
        self.assertFalse(self.another_simple_messenger_signal_was_called)

        ##################
        # 2.2: Must just call the first one signal
        self.init_simple_messenger_check_signal()
        self.init_another_simple_messenger_check_signal()

        #       Take action:
        csignal.send_robust(sender=TestModel1, parameter1='test')

        #       Check the first one is called
        self.assertTrue(self.simple_messenger_signal_was_called)
        self.assertEqual(self.simple_messenger_trigger_context['verb'], 'csignal')
        self.assertEqual(self.simple_messenger_trigger_context['action_object_content_type'],
                         ContentType.objects.get_for_model(TestModel1))

        #       Check second one isn't called
        self.assertFalse(self.another_simple_messenger_signal_was_called)

        ##################
        # 2.3: Must call both signals
        self.init_simple_messenger_check_signal()
        self.init_another_simple_messenger_check_signal()

        #       Take action:
        csignal.send_robust(sender=TestModel1, actor_object=TestModel2, parameter1='test')

        #       Check the first one is called
        self.assertTrue(self.simple_messenger_signal_was_called)
        self.assertEqual(self.simple_messenger_trigger_context['verb'], 'csignal')
        self.assertEqual(self.simple_messenger_trigger_context['action_object_content_type'],
                         ContentType.objects.get_for_model(TestModel1))

        #       Check the second one is called
        self.assertTrue(self.another_simple_messenger_signal_was_called)
        self.assertEqual(self.another_simple_messenger_trigger_context['verb'], 'csignal')
        self.assertEqual(self.another_simple_messenger_trigger_context['action_object_content_type'],
                         ContentType.objects.get_for_model(TestModel1))
        self.assertEqual(self.another_simple_messenger_trigger_context['actor_object_content_type'],
                         ContentType.objects.get_for_model(TestModel2))

    def test_correlative_signals(self):
        '''
        Just for testing three previous functions all together
        '''
        self.test_correlative_csignal_csignalWithActionObj_trigger_class()
        self.test_correlative_csignal_csignalWithActorObj_trigger_class()
        self.test_correlative_csignalWithActionObj_csignalWithActionActorObj_trigger_class
