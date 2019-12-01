from django.conf import settings

# Module name to search django_signal_notifier preferences in.
APP_MODULE_NAME = getattr(settings, 'DSN_APP_MODULE_NAME', 'django_signal_notifier')

# Set it True if you want to get more verbose
DEBUG_MODE = getattr(settings, 'DSN_DEBUG_MODE', False)

# Change default django Uesr model
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', "auth.User")

# # Change default Profile model (Note: Change your admin page of user model to show profile)
PROFILE_MODEL = getattr(settings, 'DSN_PROFILE_MODEL', "django_signal_notifier.DSN_Profile")


