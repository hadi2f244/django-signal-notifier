============
Settings
============

* ``AUTH_USER_MODEL`` :
  ``auth.User`` is used as default user model.
  It must be a string in the format of *'app_name.user_model'*

* ``PROFILE_MODEL`` :
  According to `the Django documentation <https://docs.djangoproject.com/en/3.0/topics/auth/customizing/>`_, there are some ways to extend user model. But the simplest and extendable one is creating a user profile model that has a one-to-one connection to the 'auth.user' model.
  We defined a profile model as follow, You can change it in the format of *'app_name.user_model'*.

  .. code-block:: python

    class DSN_Profile(models.Model):
        user = models.OneToOneField(to=app_settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        telegram_chat_id = models.CharField(max_length=20, blank=True, null=True)
