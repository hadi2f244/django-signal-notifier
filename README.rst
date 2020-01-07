=========================================
Introduction
=========================================

**DSN** or `django-signal-notifier <https://github.com/hadi2f244/django-signal-notifier>`_ is a Django app to send message or notification based on the Django's signals triggering. You can assign some backends to each signal(e.g. An In-Site notification app).

The major difference between ``django-signal-notifier`` and other Django's notification packages:

* ``django-signal-notifier`` is an ###

Concepts
========

**DSN**'s architecture :

    <p align="center">
    <img src="https://github.com/hadi2f244/django-signal-notifier/docs/source/_static/DSN_Architecture.png" alt="pushpin-abstract"/>
    </p>

In nutshell, we can say **DSN** is developed to *send message* :

    * **When and Where** ? : When a Trigger Triggered (The related signal's send function is called and the trigger's specs match).
    * **What** to send?: The message that is created to the message_template and other parameters like signal_kwargs.
    * **Whom** to send? : Send the message to the registered receivers in the subscription or the dynamic user that can be specified in the messenger.

*Note*: You should pay attention to these 3 questions, When you want to assign a new trigger to a signal.

Setup
============

Requirements
------------

- Python 2.7, 3.4, 3.5, 3.6, 3.7
- Django 1.7, 1.8, 1.9, 1.10, 1.11, 2.0, 2.1, 2.2, 3.0

Installation
------------

1. Install ``django-signal-notifier`` by pip:
::

    $ pip install django-signal-notifier

or use the source

::

    $ git clone https://github.com/hadi2f244/django-signal-notifier
    $ cd django-signal-notifier
    $ python setup.py sdist
    $ pip install dist/django-signal-notifier*

2. Add "django_signal_notifier" at the end of INSTALLED_APPS setting like this

::

    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        ...
        'django_signal_notifier',
    ]

3. ``django-signal-notifier`` configure by admin panel by default(Can be configured by code, tough)

4. Use ``python manage.py migrate`` for schema migration.

Usage
============

4. Run the development server and visit http://127.0.0.1:8000/admin/
   to create trigger(signal), backends(messenger and message_template) and subscription (you'll need the Admin app enabled).

5. You can test it like this:
    5.1. Create a trigger (verb=pre_save and action_object=TestModel1)

    5.2. Create a backend (messenger=SimplePrintMessengerTemplateBased and message_template=SimplePrintMessageTemplate)

    5.3. Create a subscription that connect the trigger and the backend. Add admin to users list.

    5.4. Run this command in manage.py shell:

        1. from django_signal_notifier.models import *
		2. TestModel1_another_instance = TestModel1.objects.create(name="new_test_model2", extra_field="extra")

    Now you should See a message when you create TestModel1. Actually creating new TestModel1 call pre_save signal. Then this signal call associated trigger handler.
    In the Trigger handler, associated backend is called. message_template with some details are sent to the backend.
    In our case we just print something. You can provide yourself messengers and message_templates.

