import sys
import smtplib
import threading
import requests
from .signals import TelegramMessageSignal, SMTPEmailSignal, SimplePrintMessengerSignal
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Todo: Creating __messengers_cls_list and messenger_names must be done at the end of interpreting this file,
#  if a new messenger implements after them, It's not show in the backend model choices. So, Find a solution!!!

# Todo: We should add some method that other developers can use and add their own messengers to the messengers list

class BaseMessenger:
	message = "This is a test message from dsn."
	test_message = "This is a test message for BaseMessenger!"

	def send(self, template, sender, users, context, **kwargs):
		print("sending messege to this users:")
		print("\n".join([user.username for user in users]))
		print(template.render(context))


def get_messenger_from_string(str):
	try:
		return getattr(sys.modules[__name__], str)
	except:
		return None


class SimplePrintMessenger(BaseMessenger):
	message = "SimplePrintMessenger send function has run."

	@classmethod
	def send(self, template, sender, users, context, **kwargs):
		# print("sending messege to this users:")
		# print("\n".join([user.username for user in users]))
		# print(template.render(context))
		print(self.message)
		SimplePrintMessengerSignal.send_robust(sender=self, response=True, sender_=sender, users=users, context=context, kwargs=kwargs)



class SMTPEmailMessenger(BaseMessenger):

	@classmethod
	def send_notification_email(cls, username, password, receiver_emails, email_texts, email_context, host, port):
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
			print("unable to connect to SMTP server\nError text: {error_text}".format(error_text=e))
			return

		for i, email in enumerate(receiver_emails):
			message = MIMEMultipart('alternative')
			message["Subject"] = "This is a notification from dsn"
			message["From"] = username
			text = MIMEText(email_texts[i], "html")
			message.attach(text)

			message["To"] = email
			response = True
			try:
				server.sendmail(username, email, message.as_string())
				print("Email sent to {}".format(email))
			except Exception as e:
				print(e)
				response = False
			SMTPEmailSignal.send_robust(sender=cls, response=response)


	def send(self, template, sender, users, context, **kwargs):
		"""
		Method used to send emails to given list of emails.

		:return:
		"""
		# WARNING!
		# keep this 2 secret and away from production!
		sender_username = "hamgard.invitation@gmail.com"
		sender_password = "Tahlil9798"

		# Default email service host address and port:
		host = "smtp.gmail.com"
		port = 465
		receiver_emails = [user.email for user in users if (user.email is not None) and (user.email != "")]

		email_texts = []
		for user in users:  # Add user to the context and create related email_text
			context['user'] = user
			email_texts.append(template.render(context))

		notification_thread = threading.Thread(target=SMTPEmailMessenger.send_notification_email,
		                                       args=[sender_username,
		                                             sender_password,
		                                             receiver_emails,
		                                             email_texts,
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
		:param bot_message: message_template message to be sent to receiver.
		:param chat_ids: the ID of receivers chat with @A_H_SignalNotifierBot.
		:return: returns the response from telegram api.
		"""

		if not len(chat_ids):
			return

		bot_message.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")
		# bot_message = "hesllo"
		print(bot_message)
		send_texts = ['https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}'
		              '&parse_mode=Markdown&text={text}'.format(bot_token=bot_token, chat_id=ID, text=bot_message)
		              for ID in chat_ids]
		for request in send_texts:
			response = requests.get(request)
			print(response.json())
			TelegramMessageSignal.send_robust(sender=cls, response=response.json().get("ok"))

		return response.json()

	def send(self, template, sender, users, context, **kwargs):
		"""
		method used to send telegram messages to given chat ids.
		Note that users must start @django_signal_notifier_test_bot to obtain a a valid chat_id.
		:param template: the message_template which is used for this message.
		:param sender: the sender class of the object:
		:param receiver_chat_ids: list of user chat ids that have started chat with the bot.
		:return:
		"""
		# WARNING! keep this token secret!
		bot_token = "930091969:AAFjclfXVO0JmE184C3S0_sMVISJ0srT4ug"

		receiver_chat_ids = [user.telegram_chat_id for user in users if user.telegram_chat_id is not None]

		bot_message = template.render(context) #Todo: Should add 'user' to the context and render it
		notification_thread = threading.Thread(target=TelegramBotMessenger.telegram_bot_sendtext,
		                                       args=[bot_token,
		                                             bot_message,
		                                             receiver_chat_ids
		                                             ],
		                                       daemon=False)

		notification_thread.start()


__messengers_cls_list = [
	SimplePrintMessenger,
	SMTPEmailMessenger,
	TelegramBotMessenger
]

# register_messengers()
messenger_names = [(msng.__name__, msng.__name__) for msng in __messengers_cls_list]
