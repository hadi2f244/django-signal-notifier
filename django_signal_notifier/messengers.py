import sys
import smtplib
import threading
import requests
from .signals import TelegramMessageSignal, SMTPEmailSignal, SimplePrintMessengerSignal, SimplePrintMessengerSignalTemplateBased
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Todo: Creating __messengers_cls_list and messenger_names must be done at the end of interpreting this file,
#  if a new messenger implements after them, It's not show in the backend model choices. So, Find a solution!!!

# Todo: We should add some method that other developers can use and add their own messengers to the messengers list

class BaseMessenger:
	message = "This is a test message from dsn."
	test_message = "This is a test message for BaseMessenger!"

	def send(self, template, sender, users, trigger_context, signal_kwargs):
		pass


def get_messenger_from_string(str):
	try:
		return getattr(sys.modules[__name__], str)
	except:
		return None


class SimplePrintMessenger(BaseMessenger):
	message = "SimplePrintMessenger send function has run."

	@classmethod
	def send(self, template, users, trigger_context, signal_kwargs):
		# print("sending messege to this users:")
		# print("\n".join([user.username for user in users]))
		# print(template.render(context))
		print(self.message)

		SimplePrintMessengerSignal.send_robust(sender=self, responses=[True for _ in range(len(users))], users=users, trigger_context=trigger_context, signal_kwargs=signal_kwargs)


class SimplePrintMessengerTemplateBased(BaseMessenger):

	@classmethod
	def send(self, template, users, trigger_context, signal_kwargs):
		# print("sending message to this users:")
		# print("\n".join([user.username for user in users]))
		for user in users:
			message = template.render(user=user, trigger_context=trigger_context, signal_kwargs=signal_kwargs)
			print(message)

		SimplePrintMessengerSignalTemplateBased.send_robust(sender=self, responses=[True for _ in range(len(users))], users=users, trigger_context=trigger_context, signal_kwargs=signal_kwargs)


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

		responses = []
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
			responses.append(response)
		SMTPEmailSignal.send_robust(sender=cls, responses=responses)

	def send(self, template, sender, users, trigger_context, signal_kwargs):
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
			email_texts.append(template.render(user, trigger_context, signal_kwargs))

		notification_thread = threading.Thread(target=SMTPEmailMessenger.send_notification_email,
		                                       args=[sender_username,
		                                             sender_password,
		                                             receiver_emails,
		                                             email_texts,
		                                             signal_kwargs,
		                                             host,
		                                             port],
		                                       daemon=False)
		notification_thread.start()


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
			              '&parse_mode=Markdown&text={text}'.format(bot_token=bot_token, chat_id=user.telegram_chat_id, text=text)

			response = requests.get(request)
			print(response.json())
			responses.append(response.json().get("ok"))

		TelegramMessageSignal.send_robust(sender=cls, responses=responses)

		return response.json()

	def send(self, template, sender, users, trigger_context, signal_kwargs):
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

		users = [user for user in users if hasattr(user, 'telegram_chat_id')]

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
	SimplePrintMessengerTemplateBased,
	SMTPEmailMessenger,
	TelegramBotMessenger
]

# register_messengers()
messenger_names = [(msng.__name__, msng.__name__) for msng in __messengers_cls_list]
