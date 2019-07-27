import sys
import smtplib
import threading

class BaseMessenger:
    message = ""

    def send(self):
        print(self.message)


def get_messenger_from_string(str):
    try:
        return getattr(sys.modules[__name__], str)
    except:
        return None


class SimplePrintMessenger1(BaseMessenger):
    message = "Hello, world1!"


class SMTPEmailMessenger(BaseMessenger):

    @staticmethod
    def send_notification_email(username, password, receiver_emails, email_text, email_context, host, port):
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
        print(1)
        try:
            server = smtplib.SMTP_SSL(host, port)
            print(2)
            server.ehlo()
            print(3)
            server.login(username, password)
            print(4)
        except Exception as e:
            print("unable to connect to server\nError text: {error_text}".format(error_text=e))
            return

        for email in receiver_emails:
            server.sendmail(username, email, email_text)
            print("Email: ",email)

    def send(self, receiver_emails=["alijahangiri.m@gmai.com", "ajahanmm@gmail.com"], **kwargs):
        """
        method used to send emails to given list of emails.

        :return:
        """
        # WARNING!
        # keep this 2 secret and away from production!
        sender_username = "hamgard.invitation@gmail.com"
        sender_password = "Tahlil9798"

        # Simple email text to be sent to receivers.
        # Format the text using kwargs either now or in send_notification_email method.
        email_text = "Test Mail for django_signal_notifier"

        # Default email service host address and port:
        host = "smtp.gmail.com"
        port = 465

        invitation_thread = threading.Thread(target=SMTPEmailMessenger.send_notification_email,
                                             args=[sender_username,
                                                   sender_password,
                                                   receiver_emails,
                                                   email_text,
                                                   kwargs,
                                                   host,
                                                   port],
                                             daemon=False)
        print(10)
        invitation_thread.start()


__messengers_cls_list = [
    SimplePrintMessenger1,
    SMTPEmailMessenger,
]

# register_messengers()
Messengers_name = [(msng.__name__, msng.__name__) for msng in __messengers_cls_list]
