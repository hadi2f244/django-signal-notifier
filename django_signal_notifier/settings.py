from django.conf import settings

# Set it True if you want to get more verbose
DEBUG_MODE = getattr(settings, 'DSN_DEBUG_MODE', False)

# Change default django Uesr model
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', "auth.User")

# # Change default Profile model (Note: Change your admin page of user model to show profile)
PROFILE_MODEL = getattr(settings, 'DSN_PROFILE_MODEL', "django_signal_notifier.DSN_Profile")


