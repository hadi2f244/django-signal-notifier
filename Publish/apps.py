import datetime
import logging

import requests
from django.apps import AppConfig

from Publish.signals import book_published, book_pre_published
from django_signal_notifier.exceptions import MessageTemplateError
from django_signal_notifier.message_templates import BaseMessageTemplate, Add_Message_Template
from django_signal_notifier.messengers import BaseMessenger, Add_Messenger

logger = logging.getLogger(__name__)


class NewMessenger(BaseMessenger):
    message = "This is a new messenger!"

    @classmethod
    def send(self, template, users, trigger_context, signal_kwargs):
        logger.info(self.message)


class NewMessageTemplate(BaseMessageTemplate):
    required_signal_args = ['instance', 'who']
    file_name = ""
    template_string = """
			{% if \"verb\" in context and context.verb != None %}
				<div>
					<p>{{ context.verb }}</p>
				</div>
			{% endif %}
			{% if \"action_object\" in context and context.action_object != None %}
				<div>
					<p>{{ context.action_object }}</p>
				</div>
			{% endif %}
			{% if \"current_time\" in context and context.current_time != None %}
				<div>
					<p>{{ context.current_time }}</p>
				</div>
			{% endif %}
			
			{% if "my_ip" in context and context.my_ip != None %}
				<div>
					<p>Your IP address: {{ context.my_ip }}</p>
				</div>
			{% endif %}
			"""

    def get_template_context(self, context):
        context['current_time'] = str(datetime.datetime.now().date())
        try:
            # context['my_ip'] = requests.get("http://ifconfig.co/ip").text
            context['my_ip'] = "127.0.0.1"
        except Exception as e:
            raise MessageTemplateError("An error on getting ip. ") from e
        return context


class PublishConfig(AppConfig):
    name = 'Publish'

    def ready(self):
        from django_signal_notifier.models import Trigger

        Add_Messenger(NewMessenger)
        Add_Message_Template(NewMessageTemplate)

        Trigger.registered_verb_signal("book_published", book_published)
        Trigger.registered_verb_signal("book_pre_published", book_pre_published)
