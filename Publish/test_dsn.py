from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from Publish.models import Book


def presave_trigger_details():
    """

    :return: A dictionary, signal or verb is set as the key and signal_kwargs is set as value.
    """
    verb_name1 = "pre_save"
    signal_kwargs1 = {
        'sender': Book,
        'instance': Book.objects.all()[0],
        'raw': None,
        'using': None,
        'update_fields': None,
    }

    verb_name2 = "pre_delete"
    signal_kwargs2 = {
        'sender': Book,
        'instance': Book.objects.all()[0],
    }

    trigger_details = {
        verb_name1: signal_kwargs1,
        verb_name2: signal_kwargs2,
    }

    return trigger_details


def simpleprint_message_template_details():
    """
    :return: A dictionary, name of message_template class is set as the key and
                value is a dictionary that contains user, trigger_context and signal_kwargs respectively
    """

    UserModel = get_user_model()

    # Details of a message_template
    message_template1 = "SimplePrintMessageTemplate"
    user1 = UserModel.objects.all()[0]
    trigger_context1 = {
        'verb': 'test_signal',
        'action_object': Book,
        'action_object_content_type': ContentType.objects.get_for_model(Book),
        'actor_object': None,
        'actor_object_content_type': None,
        'target': None,
    }
    signal_kwargs1 = {
        'sender': Book,
        'instance': None,
    }

    # Details of another template message
    message_template2 = "AnotherSimplePrintMessenger"
    user2 = UserModel.objects.all()[0]
    trigger_context2 = {
        'verb': 'test_signal',
        'action_object': Book.objects.all()[0],
        'action_object_content_type': ContentType.objects.get_for_model(Book),
        'actor_object': None,
        'actor_object_content_type': None,
        'target': None,
    }
    signal_kwargs2 = {
        'sender': Book,
        'instance': Book.objects.all()[0],
    }



    # Details of another template message
    message_template3 = "NewMessageTemplate"
    user3 = UserModel.objects.all()[0]
    trigger_context3 = {
        'verb': 'test_signal',
        'action_object': Book.objects.all()[0],
        'action_object_content_type': ContentType.objects.get_for_model(Book),
        'actor_object': None,
        'actor_object_content_type': None,
        'target': None,
    }
    signal_kwargs3 = {
        'sender': Book,
        'instance': Book.objects.all()[0],
    }

    message_templates_details = {
        message_template1: {
            'user': user1,
            'trigger_context': trigger_context1,
            'signal_kwargs': signal_kwargs1,
        },
        message_template2: {
            'user': user2,
            'trigger_context': trigger_context2,
            'signal_kwargs': signal_kwargs2,
        },
        message_template3: {
            'user': user3,
            'trigger_context': trigger_context3,
            'signal_kwargs': signal_kwargs3,
        },
    }

    return message_templates_details
