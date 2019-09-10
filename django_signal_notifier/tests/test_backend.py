# import time
#
# from django_signal_notifier.messengers import SMTPEmailMessenger, TelegramBotMessenger
# from django_signal_notifier.models import *
# from django_signal_notifier.signals import TelegramMessageSignal, SMTPEmailSignal
# from django_signal_notifier.tests.test_basic import SignalNotifierTestBase
#
#
# class TriggerTestCase(SignalNotifierTestBase):
#
# 	def init_telegram_messenger_check_signal(self):
# 		self.telegram_signal_was_called = False
# 		self.telegram_response = None
#
# 		def telegram_message_handler(sender, response, **kwargs):
# 			"""
# 			this functions handles sent telegram messages. when a telegram message is sent,
# 			 a signal(TelegramMessegeSignal) is sent. this function receives the signal and updates test status.
# 			 test status is checked via assertions below.
# 			:param sender: sender class of the signal. In this case, the sender is TelegramBotMessenger.
# 			:param response: if the message is delivered this param is True.
# 			:param kwargs: ...
# 			:return:
# 			"""
# 			self.telegram_signal_was_called = True
# 			self.telegram_response = response
#
# 		self.telegram_message_handler = telegram_message_handler
# 		TelegramMessageSignal.connect(self.telegram_message_handler, sender=TelegramBotMessenger)
#
# 	def init_smtp_messenger_check_signal(self):
#
# 		self.smtp_signal_was_called = False
# 		self.smtp_response = False
# 		def smtp_email_handler(sender, response, **kwargs):
# 			"""
# 			this function handles sent smtp emails. when an email is successfully sent a signal is sent from
# 			 SMTPEmailMessenger. this function handles te signal and updates test status accordingly.
# 			:param sender: sender class of the signal. In this case it is SMTPEmailMessenger.
# 			:param response: the response provided by the signal sender class
# 			:param kwargs: ...
# 			:return:
# 			"""
# 			self.smtp_signal_was_called = True
# 			self.smtp_response = response
# 		self.smtp_email_handler = smtp_email_handler
# 		SMTPEmailSignal.connect(self.smtp_email_handler, sender=SMTPEmailMessenger)
#
# 	def test_telegram_backend(self):
# 		"""
#
# 		"""
#
# 		self.init_telegram_messenger_check_signal()
# 		telegram_backend = Backend.objects.create(messenger="TelegramBotMessenger")
#
# 		telegram_backend.send_message(sender=None, users=BasicUser.objects.all(), context={})
#
# 		# Wait for telegram api to send the message.
# 		telegram_sleep_time = 5
# 		time.sleep(telegram_sleep_time)
#
# 		self.assertTrue(self.telegram_response, msg="Check your telegram connection first.")
# 		self.assertTrue(self.telegram_signal_was_called)
#
# 	def test_smtp_backend(self):
# 		"""
#
# 		"""
#
# 		self.init_smtp_messenger_check_signal()
# 		smtp_backend = Backend.objects.create(messenger="SMTPEmailMessenger")
#
# 		smtp_backend.send_message(sender=None, users=BasicUser.objects.all(), context={})
#
# 		email_sleep_time = 10
# 		time.sleep(email_sleep_time)
#
# 		self.assertTrue(self.smtp_signal_was_called, msg="Check your connection to the smtp server.")
# 		self.assertTrue(self.smtp_response)
