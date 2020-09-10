import logging
import smtplib
import threading
from typing import Any, Mapping
import requests
from django.utils.translation import gettext as _
from django.utils.html import strip_tags

from django_signal_notifier.message_templates import BaseMessageTemplate
from django.conf import settings
from .exceptions import MessengerError
from .signals import TelegramMessageSignal, SMTPEmailSignal, SimplePrintMessengerSignal, \
    SimplePrintMessengerSignalTemplateBased, AnotherSimplePrintMessengerSignal
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


class BaseMessenger:
    message = "This is a test message from dsn."
    test_message = "This is a test message for BaseMessenger!"

    @classmethod
    def send(self, template, users, trigger_context, signal_kwargs):
        pass

    @classmethod
    def test_send(self, user_identification, test_message):
        pass


class SimplePrintMessenger(BaseMessenger):
    message = "Send function of SimplePrintMessenger has run."

    @classmethod
    def send(self, template, users, trigger_context, signal_kwargs):
        logger.warning(self.message)

        SimplePrintMessengerSignal.send_robust(sender=self, responses=[True for _ in range(len(users))], users=users,
                                               trigger_context=trigger_context, signal_kwargs=signal_kwargs)

    @classmethod
    def test_send(self, user_identification, test_message):
        logger.warning(
            f"SimplePrintMessenger has run for {user_identification}(as the user_identification),\n The message:\n {test_message}")


class AnotherSimplePrintMessenger(BaseMessenger):
    message = "Send function of AnotherSimplePrintMessenger has run."

    @classmethod
    def send(self, template, users, trigger_context, signal_kwargs):
        logger.warning(self.message)

        AnotherSimplePrintMessengerSignal.send_robust(sender=self, responses=[True for _ in range(len(users))],
                                                      users=users, trigger_context=trigger_context,
                                                      signal_kwargs=signal_kwargs)


class SimplePrintMessengerTemplateBased(BaseMessenger):

    @classmethod
    def send(self, template, users, trigger_context, signal_kwargs):
        for user in users:
            message = template.render(user=user, trigger_context=trigger_context, signal_kwargs=signal_kwargs)
            logger.warning(message)

        SimplePrintMessengerSignalTemplateBased.send_robust(sender=self, responses=[True for _ in range(len(users))],
                                                            users=users, trigger_context=trigger_context,
                                                            signal_kwargs=signal_kwargs)


class SMTPEmailMessenger(BaseMessenger):
    # We have copied some parts of the code from django-sitemessage package
    # https://github.com/idlesign/django-sitemessage/blob/master/sitemessage/messengers/smtp.py

    def __init__(self):

        self.server_email = getattr(settings, 'SERVER_EMAIL')
        self.host_user = getattr(settings, 'EMAIL_HOST_USER')
        self.host_password = getattr(settings, 'EMAIL_HOST_PASSWORD')
        self.host = getattr(settings, 'EMAIL_HOST')
        self.port = getattr(settings, 'EMAIL_PORT')
        self.use_tls = getattr(settings, 'EMAIL_USE_TLS')
        self.use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)  # False as default to support Django < 1.7
        self.timeout = getattr(settings, 'EMAIL_TIMEOUT', None)  # None as default to support Django < 1.8
        self.debug = getattr(settings, 'DEBUG', True)

    def _build_message(self, user_email, text, subject=None, mtype=None, unsubscribe_url=None):
        if subject is None:
            subject = '%s' % _('No Subject')

        if mtype == 'html':
            msg = MIMEMultipart()
            text_part = MIMEMultipart('alternative')
            text_part.attach(MIMEText(strip_tags(text), _charset='utf-8'))
            text_part.attach(MIMEText(text, 'html', _charset='utf-8'))
            msg.attach(text_part)

        else:
            msg = MIMEText(text, _charset='utf-8')

        msg['From'] = self.server_email
        msg['To'] = user_email
        msg['Subject'] = subject

        if unsubscribe_url:
            msg['List-Unsubscribe'] = '<%s>' % unsubscribe_url

        return msg

    def _build_message_from_template(self, template, user, trigger_context: Mapping[str, Any],
                                     signal_kwargs: Mapping[str, Any]):
        """Constructs a MIME message from massage."""

        rendered_text = template.render(user, trigger_context, signal_kwargs)

        try:
            subject = template.get_subject(rendered_text)
            text = template.get_text(rendered_text)
        except AttributeError:
            logger.error("Incompatible message_template. It must have get_subject and get_text methods.")
            return None
        return self._build_message(user.email, text, subject=subject)

    def _connect_to_server(self):
        # 1. Connecting to smtp server
        try:
            smtp_cls = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
            kwargs = {}
            timeout = self.timeout

            if timeout:
                kwargs['timeout'] = timeout

            self.smtp = smtp_cls(self.host, self.port, **kwargs)

            if self.debug:
                self.smtp.set_debuglevel(2)

            if self.use_tls:
                self.smtp.ehlo()
                if self.smtp.has_extn('STARTTLS'):
                    self.smtp.starttls()
                    self.smtp.ehlo()  # This time over TLS.

            if self.host_user:
                self.smtp.login(self.host_user, self.host_password)

            return True

        except smtplib.SMTPException as e:
            logger.error('SMTP Error: <%s>, Check the SMTP configs in settings.py' % e)
            return False

    @classmethod
    def _send_message_poll(cls, smtp, msgs):

        responses = []
        for msg in msgs:
            responses.append(SMTPEmailMessenger1._send_message(smtp, msg))

        # Disconnecting the smtp connection
        smtp.quit()
        SMTPEmailSignal.send_robust(sender=cls, responses=responses)

    @classmethod
    def _send_message(cls, smtp, msg) -> bool:
        try:
            smtp.sendmail(msg['From'], msg['To'], msg.as_string())
            email = msg['To']
            logger.info(f"Email sent to {email}")
            return True
        except Exception as e:
            logger.error(f"Sending mail error:{e}")
            return False

    @classmethod
    def test_send(cls, user_identification, test_message):  # user_identification is the email address
        instance = cls()
        email_message = instance._build_message(user_identification, test_message, mtype='html')

        instance.send_emails([email_message])
        logger.warning(
            f"SimplePrintMessenger has run for {user_identification}(as the user_identification),\n The message:\n {test_message}")

    def send_emails(self, email_messages):
        """
            function used for sending emails using smtplib. this function must be given to a thread as target in order
            to avoid performance and response issues.

            :param receiver_emails: target emails for the email to be sent to
            :param email_messages: email text to be sent to targets
            :param email_context: email text must be formatted using the context given
            :param host: host url of the email service provider
            :param port: port of host address used to send emails
            :return:
        """

        # 1. Connect to smpt server
        if self._connect_to_server():
            # 2. Send mails
            send_message_poll_thread = threading.Thread(target=SMTPEmailMessenger1._send_message_poll,
                                                        args=[self.smtp,
                                                              email_messages],
                                                        daemon=False)
            send_message_poll_thread.start()

        # try:
        #     server = smtplib.SMTP_SSL(host, port)
        #     server.ehlo()
        #     server.login(username, password)
        # except Exception as e:
        #     logger.error(f"Unable to connect to SMTP server\n   Error: {e}")
        #     return
        # email = EmailMessage('Header', None, to=['user@gmail.com'])
        # email.send()
        # responses = []
        # for i, email in enumerate(receiver_emails):
        #     message = MIMEMultipart('alternative')
        #     message["Subject"] = "This is a notification from dsn"
        #     message["From"] = username
        #     text = MIMEText(email_texts[i], "html")
        #     message.attach(text)
        #
        #     message["To"] = email
        #     response = True
        #     try:
        #         server.sendmail(username, email, message.as_string())
        #         logger.info(f"Email sent to {email}")
        #     except Exception as e:
        #         logger.error(f"Sending mail error:{e}")
        #         response = False
        #     responses.append(response)

    def send(self, template: BaseMessageTemplate, users, trigger_context: Mapping[str, Any],
             signal_kwargs: Mapping[str, Any]):
        """
            Method used to send emails to given list of emails.
        """

        # Checking message_template and messenger compatibility
        msg = self._build_message_from_template(template, users[0], trigger_context, signal_kwargs)
        if msg is None:
            return

        # Sending messages
        email_messages = []
        for user in users:  # Add user to the context and create related email_text
            msg = self._build_message_from_template(template, user, trigger_context, signal_kwargs)
            email_messages.append(msg)

        self.send_emails(email_messages)


class TelegramBotMessenger(BaseMessenger):

    # Todo: add capability to add another telegram bot
    @classmethod
    def telegram_bot_sendtext(cls, bot_token, template, users, trigger_context, signal_kwargs):
        """
            Sends messages and notifications using telegram api and @A_H_SignalNotifierBot
            https://t.me/A_H_SignalNotifierBot

            :param bot_token: the token of the bot used to send messages. default bot is @A_H_SignalNotifierBot.
            :param template: message_template message to be sent to receiver.
            :param users: list of users.
            :param trigger_context: trigger_context that is sent from trigger
            :param signal_kwargs: signal_kwargs that are sent from trigger
            :return: returns the response from telegram api.
        """

        if not len(users):
            return

        # bot_message = "hesllo"

        responses = []
        for user in users:
            text = template.render(user, trigger_context, signal_kwargs)

            # It doesn't work well
            text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

            request = 'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}' + \
                      '&parse_mode=Markdown&text={text}'.format(bot_token=bot_token,
                                                                chat_id=user.dsn_profile.telegram_chat_id, text=text)

            response = requests.get(request)
            responses.append(response.json().get("ok"))

        TelegramMessageSignal.send_robust(sender=cls, responses=responses)

        return response.json()

    def send(self, template, users, trigger_context, signal_kwargs):
        """
            method used to send telegram messages to given chat ids.
            Note that users must start @django_signal_notifier_test_bot to obtain a a valid chat_id.
            :param template: the message_template which is used for this message.
            :param receiver_chat_ids: list of user chat ids that have started chat with the bot.
            :return:
        """

        # Todo: WARNING! keep this token secret!
        bot_token = "930091969:AAFjclfXVO0JmE184C3S0_sMVISJ0srT4ug"

        users = [user for user in users if hasattr(user.dsn_profile, 'telegram_chat_id')]

        # receiver_chat_ids = [user.telegram_chat_id for user in users if user.telegram_chat_id is not None]
        # bot_message = template.render(user, trigger_context, signal_kwargs)

        notification_thread = threading.Thread(target=TelegramBotMessenger.telegram_bot_sendtext,
                                               args=[bot_token,
                                                     template,
                                                     users,
                                                     trigger_context,
                                                     signal_kwargs,
                                                     ],
                                               daemon=False)

        notification_thread.start()


__messengers_cls_list = [
    SimplePrintMessenger,
    AnotherSimplePrintMessenger,
    SimplePrintMessengerTemplateBased,
    SMTPEmailMessenger,
    TelegramBotMessenger
]
messenger_names = []
__messenger_classes = {}

for msng in __messengers_cls_list:
    messenger_names.append((msng.__name__, msng.__name__))
    __messenger_classes[msng.__name__] = msng


def Add_Messenger(messenger_class):
    """
    Add new messenger to message_template lists
    :param messenger_class: A messenger class that inherited from BaseMessenger
    :return:
    """

    global __messengers_cls_list, messenger_names, __messenger_classes
    if not issubclass(messenger_class, BaseMessenger):
        raise MessengerError("Every messenger class must inherit from django_signal_notifier.messengers.BaseMessenger")
    __messengers_cls_list.append(messenger_class)
    messenger_names.append((messenger_class.__name__, messenger_class.__name__))
    __messenger_classes[messenger_class.__name__] = messenger_class


def get_messenger_from_string(class_name: str) -> BaseMessenger:
    global __messenger_classes
    try:
        return __messenger_classes[class_name]
    except KeyError:
        logging.warning(f"Not registered messenger, messenger name: {class_name}")
        return None
