from django.dispatch import Signal

TelegramMessageSignal = Signal(providing_args=["response_is_ok"])
