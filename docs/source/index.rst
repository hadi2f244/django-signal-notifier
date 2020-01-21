.. django_signal_notifier documentation master file, created by
   sphinx-quickstart on Mon Jan  6 20:28:51 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django_signal_notifier
==================================================

**DSN** or `django-signal-notifier <https://gitlab.com/hadiazaddel/django-signal-notifier>`_ is a Django app to send message or notification based on the Django's signals triggering. You can assign some backends to each signal(e.g. An In-Site notification app).

The major difference between ``django-signal-notifier`` and other Django's notification packages is that *DSN* isn't just a simple message delivering system.
It can act as a middleware between Django and every messenger client (Various clients like email, telegram, SMS and twitter).

It's working with event methodology, and it's based on `Django signal <https://docs.djangoproject.com/en/3.0/topics/signals/>`_. If a signal triggers, A messenger is called to send a message for specified users.
To understand how it works, We explain some main concepts at first.

Table of Contents
-----------------

.. toctree::
    :maxdepth: 2

   quickstart
   introduction
   setup
   usage
   backends
   dynamic_user
   background_task
   settings
   comparison

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`
