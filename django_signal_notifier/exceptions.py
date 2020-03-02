from django.core.exceptions import ObjectDoesNotExist


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


class TriggerValidationError(DSNException):
    """ Raise when a user want to create an invalid trigger from admin panel or code manually """
    pass


class ContentTypeObjectDoesNotExist(ObjectDoesNotExist, DSNException):
    """ Raise when access to an object that does not exist is attempted from content type in DSN"""
    pass
