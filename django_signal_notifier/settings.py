from django.conf import settings

# Module name to search sitemessage preferences in.
APP_MODULE_NAME = getattr(settings, 'DSN_APP_MODULE_NAME', 'django_signal_notifier')

# Module name to search sitemessage preferences in.
DEBUG_MODE = getattr(settings, 'DSN_DEBUG_MODE', False)

# Change AUTH_USER_MODEL to Django_signal_notifier BasicUser
AUTH_USER_MODEL = getattr(settings, 'DSN_AUTH_USER_MODEL', "django_signal_notifier.BasicUser")

# Notice it in the documentation that AUTH_USER_MODEL must set to django_signal_notifier.BasicUser too.
# MAIN_AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', AUTH_USER_MODEL)

