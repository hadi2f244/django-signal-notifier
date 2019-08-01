import sys
import smtplib
import threading
import requests
from .signals import TelegramMessageSignal, SMTPEmailSignal


class BaseMessenger:
    message = ""
    test_message = "This is a test message for BaseMessenger!"

    def send(self, sender, users,  **kwargs):
        print("sending", self.message, "to this users:")
        print("\n".join([user.username for user in users]))


def get_messenger_from_string(str):
    try:
        return getattr(sys.modules[__name__], str)
    except:
        return None


class SimplePrintMessenger1(BaseMessenger):
    message = "Hello, world1!"


class SMTPEmailMessenger(BaseMessenger):

    @classmethod
    def send_notification_email(cls, username, password, receiver_emails, email_text, email_context, host, port):
        """
        function used for sending emails using smtplib. this function must be given to a thread as target in order
        to avoid performance and response issues.

        :param username: username of the sender
        :param password: password of the sender
        :param receiver_emails: target emails for the email to be sent to
        :param email_text: email text to be sent to targets
        :param email_context: email text must be formatted using the context given
        :param host: host url of the email service provider
        :param port: port of host address used to send emails
        :return:
        """
        try:
            server = smtplib.SMTP_SSL(host, port)
            server.ehlo()
            server.login(username, password)
        except Exception as e:
            print("unable to connect to server\nError text: {error_text}".format(error_text=e))
            return
        for email in receiver_emails:
            response = True
            try:
                server.sendmail(username, email, email_text)
            except:
                response = False
            SMTPEmailSignal.send_robust(sender=cls, response_is_ok=response)

    def send(self, sender, users, **kwargs):
        """
        Method used to send emails to given list of emails.

        :return:
        """
        # WARNING!
        # keep this 2 secret and away from production!
        sender_username = "hamgard.invitation@gmail.com"
        sender_password = "Tahlil9798"

        # Simple email text to be sent to receivers.
        instance = kwargs.get('instance')
        instance_dict = instance.__dict__
        instance_spec = str(instance.__class__) + "\n"
        for key in instance_dict.keys():
            if key == "_state":
                continue
            instance_spec += str(str(key) + " : " + str(instance_dict[key]) + "\n")

        email_text = "Test Mail for django_signal_notifier. Have a nice day!\n{}".format(instance_spec)
        # Default email service host address and port:
        host = "smtp.gmail.com"
        port = 465

        receiver_emails = [user.email for user in users if user.email is not None]
        notification_thread = threading.Thread(target=SMTPEmailMessenger.send_notification_email,
                                               args=[sender_username,
                                                     sender_password,
                                                     receiver_emails,
                                                     email_text,
                                                     kwargs,
                                                     host,
                                                     port],
                                               daemon=False)
        notification_thread.start()


class TelegramBotMessenger(BaseMessenger):

    @classmethod
    def telegram_bot_sendtext(cls, bot_token, bot_message, chat_ids):  # Chat_id defaults to @alijhnm.
        """
        Sends messages and notifications using telegram api and @A_H_SignalNotifierBot
        https://t.me/A_H_SignalNotifierBot

        :param bot_token: the token of the bot used to send messages. default bot is @A_H_SignalNotifierBot.
        :param bot_message: template message to be sent to receiver.
        :param chat_ids: the ID of receivers chat with @A_H_SignalNotifierBot.
        :return: returns the response from telegram api.
        """

        if not len(chat_ids):
            return

        send_texts = ['https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}'
                      '&parse_mode=Markdown&text={text}'.format(bot_token=bot_token, chat_id=ID, text=bot_message)
                      for ID in chat_ids]

        for request in send_texts:
            response = requests.get(request)
            print(response.json())
            TelegramMessageSignal.send_robust(sender=cls, response_is_ok=response.json().get("ok"))

        return response.json()

    def send(self, sender, users, **kwargs):
        """
        method used to send telegram messages to given chat ids.
        Note that users must start @A_H_SignalNotifierBot to obtain a a valid chat_id.
        :param sender: the sender class of the object:
        :param receiver_chat_ids: list of user chat ids that have started chat with the bot.
        :return:
        """

        # WARNING! keep this token secret!
        bot_token = "965146571:AAHWKsTUOia8NWXc6X_SfO13SdvmT2maEHo"

        # Template message to be sent as notification message:
        instance = kwargs.get('instance')
        instance_dict = instance.__dict__
        instance_spec = ""

        # Uncomment these lines so that the messege will not be sent.

        # for key in instance_dict.keys():
        #     if key == "_state":
        #         continue
        #     instance_spec += str(str(key) + " : " + str(instance_dict[key]) + "\n")
        receiver_chat_ids = [user.telegram_chat_id for user in users if user.telegram_chat_id is not None]
        bot_message = "This is a test message from django-signal-notifier Have a nice day!\n{}".format(instance_spec)
        notification_thread = threading.Thread(target=TelegramBotMessenger.telegram_bot_sendtext,
                                               args=[bot_token,
                                                     bot_message,
                                                     receiver_chat_ids
                                                     ],
                                               daemon=False)

        notification_thread.start()


__messengers_cls_list = [
    SimplePrintMessenger1,
    SMTPEmailMessenger,
    TelegramBotMessenger
]

# register_messengers()
Messengers_name = [(msng.__name__, msng.__name__) for msng in __messengers_cls_list]
