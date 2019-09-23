from django.apps import AppConfig
from django_signal_notifier.messengers import Add_Messenger, BaseMessenger
from django_signal_notifier.message_templates import Add_Message_Template
from .models import Messages, UpdateMessages


class InsitMessagingMessenger(BaseMessenger):
    message = "Insite Messaging "

    @classmethod
    def send(self, template, sender, users, trigger_context, signal_kwargs):
        message = template.render(user=None, trigger_context=trigger_context, signal_kwargs=signal_kwargs)
        insite_message = Messages.objects.create(context=message)
        insite_message.save()
        for user in users:
            insite_message.user_receivers.add(user)
            message = template.render(user=user, trigger_context=trigger_context, signal_kwargs=signal_kwargs)
            update_message = UpdateMessages.objects.create(user_id=user.id, context=message)
            update_message.save()


class InsiteMessagingConfig(AppConfig):
    name = 'insite_messaging'

    Add_Messenger(InsitMessagingMessenger)
