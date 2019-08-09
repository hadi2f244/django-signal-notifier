import datetime
import json
import sys

from django.template import Template, Context
from django.template.loader import render_to_string
from django.template.defaulttags import register

# Todo: Creating __message_template_cls_list and message_template_names must be done at the end of interpreting this file,
#  if a new message_template implements after them, It's not show in the backend model choices. So, Find a solution!!!

# Todo: We should add some method that other developers can use and add their own message_templates to the message_template list

def get_message_template_from_string(str):
	try:
		return getattr(sys.modules[__name__], str)
	except:
		return None


class BaseMessageTemplate:
	# When file_name isn't empty, the template_string initial value will ignored.
	# It's better to re-implement them in the classes which inherit BaseMessageTemplate
	file_name = "message_templates/base.html"
	template_string = ""

	context_template_str = "{}"

	def __init__(self):
		if (self.file_name.strip() != "" and self.template_string.strip() != ""):
			raise ValueError("One of the file_name and template_string variables must be empty")
		if (self.file_name.strip() == "" and self.template_string.strip() == ""):
			raise ValueError("One of the file_name and template_string variables must not be empty")

	@property
	def context_template(self):
		try:
			return json.loads(self.context_template_str)
		except Exception as e:
			print("Error parsing context for message_template {}.".format(self.file_name))
			return dict()

	def __str__(self):
		return self.file_name

	# Todo: Before rendering the template, we should make sure that the context is compatible with context_template_str
	# If not, It should be converted to a proper version (Set null for keys which aren't in the context while exist in context_template_str)
	def check_context_compatibility(self):
		pass

	def render(self, context=None):
		if context is None:
			context = self.context_template

		context = self.get_template_context(context)

		if (self.file_name == ""):  # render template from template_string
			tmpl = Template(self.template_string)
			ctx = Context({"context": context})
			return tmpl.render(ctx)
		else:  # render template from file
			return render_to_string(self.file_name, context={"context": context})

	def get_template_context(self, context):
		'''
		Change context as you want
		:param context: context of message_template message
		:return: Dictionary (context)
		'''
		return context

	def set_context_template_str(self, context_template_str):
		self.context_template_str = context_template_str


# def update_context(self, added_context):
# 	temp_dict = self.context_template
# 	temp_dict.update(added_context)
# 	self.context_template = json.dumps(temp_dict)


class SimpleEmailMessageTemplate(BaseMessageTemplate):
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
	# Todo: Some extra lines exist in the template string, What's the reason?

	def get_template_context(self, context):
		context['current_time'] = str(datetime.datetime.now().date())
		return context


class SimpleTelegramMessageTemplate1(BaseMessageTemplate):
	file_name = "message_templates/simple_telegram_message.html"
	template_string = ""

	def get_template_context(self, context):
		context['current_time'] = str(datetime.datetime.now().date())
		return context


class SimpleTelegramMessageTemplate2(BaseMessageTemplate):
	file_name = ""
	template_string = """
		This is another telegram message message_template which has no context variables.
    """

__message_template_cls_list = [
	BaseMessageTemplate,
	SimpleEmailMessageTemplate,
	SimpleTelegramMessageTemplate1,
	SimpleTelegramMessageTemplate2,
]

message_template_names = [(mstmpl.__name__, mstmpl.__name__) for mstmpl in __message_template_cls_list]



### Todo: How to implement some template tags and filters and use them in message templates ? e.g.:

# # Accessing value of a key in a dictionary in a template string
# @register.filter
# def get_item(dictionary, key):
# 	return dictionary.get(key)
