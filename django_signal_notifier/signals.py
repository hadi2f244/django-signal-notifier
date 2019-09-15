from django.dispatch import Signal

SimplePrintMessengerSignal = Signal(providing_args=["responses","users","trigger_context","signal_kwargs"])
SimplePrintMessengerSignalTemplateBased= Signal(providing_args=["responses","users","trigger_context","signal_kwargs"])
TelegramMessageSignal = Signal(providing_args=["responses"])
SMTPEmailSignal = Signal(providing_args=["responses"])
