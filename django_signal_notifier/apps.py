import logging
import sys

from django.apps import AppConfig
from django.db.models import signals

from django_signal_notifier.message_templates import Add_Message_Template, \
    SimplePrintMessageTemplateRequiredSignalArgs, AnotherSimplePrintMessageTemplateRequiredSignalArgs
from django_signal_notifier.signals import csignal, csignal_another

logger = logging.getLogger(__name__)


class DjangoSignalNotifierConfig(AppConfig):
    name = 'django_signal_notifier'
    verbose_name = 'django_signal_notifier'

    def ready(self):
        from django_signal_notifier.models import Trigger
        registered_verb_signal_list = {
            "pre_init": signals.pre_init,
            "post_init": signals.post_init,
            "pre_save": signals.pre_save,
            "post_save": signals.post_save,
            "pre_delete": signals.pre_delete,
            "post_delete": signals.post_delete,
            "m2m_changed": signals.m2m_changed,
            "pre_migrate": signals.pre_migrate,
            "post_migrate": signals.post_migrate,
        }
        Trigger.register_verb_signal_list(registered_verb_signal_list)

        if 'test' not in sys.argv:  # Avoid connecting predefined trigger in db for test mode
            Trigger.reconnect_all_triggers()
        else:
            Trigger.registered_verb_signal('csignal', csignal)
            Trigger.registered_verb_signal('csignal_another', csignal_another)
            Add_Message_Template(SimplePrintMessageTemplateRequiredSignalArgs)
            Add_Message_Template(AnotherSimplePrintMessageTemplateRequiredSignalArgs)
