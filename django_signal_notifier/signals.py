from django.dispatch import Signal

# Backend Test Signals;
SimplePrintMessengerSignal = Signal(providing_args=["responses", "users", "trigger_context", "signal_kwargs"])
AnotherSimplePrintMessengerSignal = Signal(providing_args=["responses", "users", "trigger_context", "signal_kwargs"])
SimplePrintMessengerSignalTemplateBased = Signal(
    providing_args=["responses", "users", "trigger_context", "signal_kwargs"])
TelegramMessageSignal = Signal(providing_args=["responses"])
SMTPEmailSignal = Signal(providing_args=["responses"])

# Custom Signals for testing DSN core:
csignal = Signal(providing_args=["parameter1"])
