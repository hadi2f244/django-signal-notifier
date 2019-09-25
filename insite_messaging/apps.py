import time

from django.apps import AppConfig
from django_signal_notifier.messengers import Add_Messenger, BaseMessenger
from django_signal_notifier.message_templates import Add_Message_Template


class InsiteMessagingConfig(AppConfig):
	name = 'insite_messaging'

	def ready(self):
		from insite_messaging.models import UpdateMessages, Messages

		class InsitMessagingMessenger(BaseMessenger):
			message = "Insite Messaging"

			@classmethod
			def send(self, template, users, trigger_context, signal_kwargs):
				message = template.render(user=None, trigger_context=trigger_context, signal_kwargs=signal_kwargs)
				insite_message = Messages.objects.create(context=message)
				insite_message.save()
				for user in users:
					insite_message.user_receivers.add(user)
					message = template.render(user=user, trigger_context=trigger_context, signal_kwargs=signal_kwargs)
					update_message = UpdateMessages(user_id=user.id, context=message)
					update_message.save()
					time.sleep(5)

		Add_Messenger(InsitMessagingMessenger)
