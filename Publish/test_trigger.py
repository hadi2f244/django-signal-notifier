from Publish.models import Book
from django_signal_notifier.models import Trigger


def presave_trigger_run():
    """

    :return: A dictionary, signal or verb is set as the keys and signal_kwargs is set as values.
    """
    verb_name1 = "pre_save"
    signal_kwargs1 = {
        'sender': Book,
        'instance': Book.objects.all()[0],
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