from django.apps import AppConfig
from django.db.models import signals
import sys

class DjangoSignalNotifierConfig(AppConfig):
	name = 'django_signal_notifier'
	verbose_name = 'django_signal_notifier'

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
		# Todo: Important, we should add custom_signal to verb_signal_list too, because after application restart we don't know the custom signal fuction !!!

		try:
			Trigger.reconnect_all_triggers()
		except:
			print("You haven't run migrate and makemigrations commands")
