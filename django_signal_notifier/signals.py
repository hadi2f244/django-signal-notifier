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
csignal_another = Signal(providing_args=["another_parameter1"])
## csignal_admin_panel = Signal(providing_args=["parameter1"])  # Just use this signal as a custom_signal in admin panel
# for testing. Avoid using this in test functions
