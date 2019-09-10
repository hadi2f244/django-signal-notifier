from django.dispatch import Signal

SimplePrintMessengerSignal = Signal(providing_args=["sender","response","sender_","users","context","kwargs"])
TelegramMessageSignal = Signal(providing_args=["response"])
SMTPEmailSignal = Signal(providing_args=["response"])
