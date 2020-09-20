import datetime
import logging

from django.template import Template, Context
from django.template.loader import render_to_string

from django_signal_notifier.exceptions import MessageTemplateError

logger = logging.getLogger(__name__)


class BaseMessageTemplate:
    # When file_name isn't empty, the template_string initial value will ignored.
    # It's better to re-implement them in the classes which inherit BaseMessageTemplate
    file_name = "message_templates/base.html"
    template_string = ""

    # list of signal arguments that are required when providing arguments in the triggers
    required_signal_args = []

    def __init__(self):
        if self.file_name.strip() != "" and self.template_string.strip() != "":
            raise MessageTemplateError("Only one of the file_name and template_string variables must be empty")
        if self.file_name.strip() == "" and self.template_string.strip() == "":
            raise MessageTemplateError("Both file_name and template_string are empty. "
                                       "One of them must not be empty")

    # @property
    # def context_template(self):
    # 	try:
    # 		return json.loads(self.context_template_str)
    # 	except Exception as e:
    # 		logger.error("Error parsing context for message_template {}.".format(self.file_name))
    # 		return dict()

    def __str__(self):
        return self.file_name

    def render(self, user, trigger_context, signal_kwargs):
        # Merging trigger_context and signal_kwargs
        context = signal_kwargs.copy()
        for key, val in trigger_context.items():
            if key in context:
                logger.error(
                    f"Conflict between trigger_context and signal_kwargs keys. \n"
                    f"trigger_context and signal_kwargs are combined together to be used in rendering message_template,"
                    f" So their keys must not overlap."
                    f" The value in trigger_context is preferred over signal_kwargs.\n"
                    f"The overlapped key: '{key}'\nMore details: "
                    f"\n   trigger_context:{trigger_context} "
                    f"\n   signal_kwargs:{signal_kwargs}"
                    f"\n")
            context[key] = val
        if 'user' in context:
            logger.error(
                f"User argument must not exists in trigger_context or signal_kwargs, Details: \n    user:{user} "
                f"\n    context['user']:{context['user']} "
                f"\n   trigger_context:{trigger_context} \n   signal_kwargs:{signal_kwargs}")
        context['user'] = user
        context = self.get_template_context(context)

        if self.file_name == "":  # render template from template_string
            tmpl = Template(self.template_string)
            ctx = Context({"context": context})
            return tmpl.render(ctx)
        else:  # render template from file
            return render_to_string(self.file_name, context={"context": context})

    def get_template_context(self, context):
        """
        Change context as you want(e.g. add current time)
        :param context: context of message_template message
        :return: a Dictionary (context)
        """

        return context


# def set_context_template_str(self, context_template_str):
# 	self.context_template_str = context_template_str


class SimplePrintMessageTemplate(BaseMessageTemplate):
    file_name = "message_templates/simple_print_message.html"
    template_string = ""


# Just for test purposes
class SimplePrintMessageTemplateRequiredSignalArgs(BaseMessageTemplate):
    file_name = "message_templates/simple_print_message.html"
    template_string = ""
    required_signal_args = ['parameter1']


# Just for test purposes
class AnotherSimplePrintMessageTemplateRequiredSignalArgs(BaseMessageTemplate):
    file_name = "message_templates/simple_print_message.html"
    template_string = ""
    required_signal_args = ['another_parameter1']

class SimpleTelegramMessageTemplate1(BaseMessageTemplate):
    file_name = "message_templates/simple_telegram_message.html"
    template_string = ""

    def get_template_context(self, context):
        context['current_time'] = str(datetime.datetime.now().date())
        return context

class SimpleTelegramMessageTemplate2(BaseMessageTemplate):
    file_name = ""

    # template_string must be in json format
    # Tips:
    #   1. Use \n at the end of each line
    #   2. don't use extra comma at last json item
    #   3. don't forget main json curly braces
    template_string = """
                               {
                                   {% if \"verb\" in context and context.verb != None %}
                                       "verb": "{{ context.verb }}",\n
                                   {% endif %}
                                   {% if \"action_object\" in context and context.action_object != None %}
                                       "action_object": "{{ context.action_object }}",\n
                                   {% endif %}
                                   {% if \"time\" in context and context.time != None %}
                                       "time": "{{ context.time }}"\n
                                   {% endif %}
                               }
                               """

    def get_template_context(self, context):
        context['time'] = str(datetime.datetime.now())

        # Add site name to the message
        from django.contrib.sites.models import Site
        site_domain = Site.objects.first().domain
        context['sitedomain'] = site_domain

        return context

    def render(self, user, trigger_context, signal_kwargs):
        rendered_string = super(SimpleTelegramMessageTemplate2, self).render(user, trigger_context, signal_kwargs)
        return rendered_string.strip()

class SimpleSMTPMessageTemplate(BaseMessageTemplate):
    file_name = ""
    template_string = """
<subject>django-signal-notifier email check</subject>

<text>
{% if \"verb\" in context and context.verb != None %}\
verb: {{ context.verb }}\
{% endif %}
{% if \"action_object\" in context and context.action_object != None %}\
action_object: {{ context.action_object }}\
{% endif %}
{% if \"current_time\" in context and context.current_time != None %}\
Time: {{ context.current_time }}\
{% endif %}
</text>
"""

    def get_subject(self, msg):
        start = msg.find("<subject>") + len("<subject>")
        end = msg.find("</subject>")
        return msg[start:end]

    def get_text(self, msg):
        start = msg.find("<text>") + len("<text>")
        end = msg.find("</text>")
        return msg[start:end]


__message_template_cls_list = [
    BaseMessageTemplate,
    SimplePrintMessageTemplate,
    SimpleTelegramMessageTemplate1,
    SimpleTelegramMessageTemplate2,
    SimpleSMTPMessageTemplate,
]

message_template_names = []
__message_template_classes = {}
for mstmpl in __message_template_cls_list:
    message_template_names.append((mstmpl.__name__, mstmpl.__name__))
    __message_template_classes[mstmpl.__name__] = mstmpl


def Add_Message_Template(message_template):
    """
    Add new message_template to message_template lists
    :param message_template: A message_template class that inherited from BaseMessageTemplate
    :return:
    """
    global __message_template_cls_list, message_template_names, __message_template_classes
    if not issubclass(message_template, BaseMessageTemplate):
        raise MessageTemplateError("Every message_template class must inherit from "
                                   "django_signal_notifier.message_templates.BaseMessageTemplate")
    __message_template_cls_list.append(message_template)
    message_template_names.append((message_template.__name__, message_template.__name__))
    __message_template_classes[message_template.__name__] = message_template


def get_message_template_from_string(class_name: str) -> BaseMessageTemplate:
    global __message_template_classes
    try:
        return __message_template_classes[class_name]
    except KeyError:
        logging.warning(f"Not registered message_template, message_template name: {class_name}")
        return None

# Todo: Implement some template tags and filters and use in message templates

# # Accessing value of a key in a dictionary in a template string
# @register.filter
# def get_item(dictionary, key):
# 	return dictionary.get(key)
