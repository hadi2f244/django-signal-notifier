from django.core.exceptions import ObjectDoesNotExist, ValidationError


class DSNException(Exception):
    """Base class for django-signal-notifier errors."""
    pass


class MessageTemplateError(DSNException):
    """ Raise then an error related to message_template occurs """
    pass


class MessengerError(DSNException):
    """ Raise then an error related to messenger occurs """
    pass


class SignalRegistrationError(DSNException):
    """ Raise when a signal can not be registered """
    pass


class ReconnectTriggersError(DSNException):
    """ Raise when reconnecting triggers to the corresponding signal results in an error.
    Note: Make sure you migrate and makemigrations first """
    pass


class TriggerValidationError(DSNException, ValidationError):
    """ Raise when a user want to create an invalid trigger from admin panel or code manually """
    pass


class ContentTypeObjectDoesNotExist(ObjectDoesNotExist, TriggerValidationError):
    """ Raise when access to an object that does not exist is attempted from content type in DSN"""
    pass


class TriggerSignalKwargsError(TriggerValidationError):
    """ Raise when an error occurs in run_corresponding_signal function"""
    pass


class MessageTemplateAndTriggerConflict(DSNException, ValidationError):
    """ Raise when required signal arguments (require_args) of a message_template aren't provided by providing_args
        of a trigger(signal) """
    pass
