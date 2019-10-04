import time

from django.apps import AppConfig
from django_signal_notifier.messengers import Add_Messenger, BaseMessenger
from django_signal_notifier.message_templates import Add_Message_Template


class InsiteMessagingConfig(AppConfig):
	name = 'insite_messaging'

	def ready(self):
		from insite_messaging.models import Messages

		class InsitMessagingMessenger(BaseMessenger):
			message = "Insite Messaging"

			@classmethod
			def send(self, template, users, trigger_context, signal_kwargs):
				for user in users:
					message = template.render(user=user, trigger_context=trigger_context, signal_kwargs=signal_kwargs)
					Messages.objects.create(user_receiver=user, context=message)

		Add_Messenger(InsitMessagingMessenger)
