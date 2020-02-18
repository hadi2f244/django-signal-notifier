import datetime
import logging

from django.apps import AppConfig

from django_signal_notifier import messengers
from django_signal_notifier.message_templates import BaseMessageTemplate, Add_Message_Template
from django_signal_notifier.messengers import BaseMessenger, Add_Messenger

logger = logging.getLogger(__name__)

class NewMessenger(BaseMessenger):
	message = "This is a new messenger!"
	@classmethod
	def send(self, template, users, trigger_context, signal_kwargs):
	    logger.info(self.message)

class NewMessageTemplate(BaseMessageTemplate):
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
			{% endif %}"""

	def get_template_context(self, context):
		context['current_time'] = str(datetime.datetime.now().date())
		return context

class PublishConfig(AppConfig):
    name = 'Publish'
    def ready(self):

	    Add_Messenger(NewMessenger)
	    Add_Message_Template(NewMessageTemplate)
