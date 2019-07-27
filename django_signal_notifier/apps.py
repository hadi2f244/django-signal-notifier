from django.apps import AppConfig
from django.db.models import signals


class DjangoSignalNotifierConfig(AppConfig):
	name = 'django_signal_notifier'

	def ready(self):
		from django_signal_notifier.models import Trigger
		init_verb_signal_list = {
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
		Trigger.set_verb_signal_list(init_verb_signal_list)
		Trigger.reconnect_all_triggers() # Comment it when you want to make migrations #Todo: comment it for migrations
