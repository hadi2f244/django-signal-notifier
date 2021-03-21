=====================================================
Django Signal Notifier
=====================================================

|docs-badge| |pypi-badge|

**DSN** or `django-signal-notifier <https://github.com/hadi2f244/django-signal-notifier>`_ is a Django package to send message or notification based on the Django's signals triggering. You can assign some backends to each signal(e.g., An In-Site notification app).

The major difference between ``django-signal-notifier`` and other Django's notification packages is that *DSN* isn't just a simple message delivering system.
It can act as a middleware between Django and every messenger client (Various clients like email, telegram, SMS and twitter).

It's working with event methodology, and it's based on `Django signal <https://docs.djangoproject.com/en/3.0/topics/signals/>`_. If a signal triggers, A messenger is called to send a message for specified users.
To understand how it works, We explain some main concepts at first.

.. attention::
    django-signal-notifier==0.2.1 is not compatible with **django>=3.1** . We are solving the problem.

Documentation, installation and getting started instructions are at `documentation`_

Concepts (Summary)
===========================

**DSN**'s architecture :

.. image:: images/DSN_Architecture.png
    :alt: DSN Architecture

In a nutshell, we can say **DSN** is developed to *send message* :

    * **When and Where** ? : When a Trigger Triggered (The associated signal's send function is called, and the trigger's specs match).
    * **What** to send?: The message that is created to the message_template and other parameters like signal_kwargs.
    * **Whom** to send? : Send the message to the registered receivers in the subscription or the dynamic user that can be specified in the messenger.

.. note::

    You should pay attention to these 3 questions when you want to assign a new trigger to a signal.


.. _Quickstart Setup:

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

4. Migrate
5. ``django-signal-notifier`` configure by admin panel by default(Can be configured by code, tough)

6. Use ``python manage.py migrate`` for schema migration.


.. _Quickstart Usage:

.. attention::

    You may face with below error, To resolve it, 'migrate' first.
        ::

            no such table: django_signal_notifier_trigger.
            An error occurs when reconnecting trigger to the corresponding signals, Note: Make sure you migrate and migrations first


Usage
============

4. Run the development server and visit http://127.0.0.1:8000/admin/
   To create a trigger(signal), backends(messenger and message_template), and subscription (you'll need the Admin app enabled).

5. You can test it like this:
    5.1. Create a trigger (verb=pre_save and action_object=TestModel1)

    5.2. Create a backend (messenger=SimplePrintMessengerTemplateBased and message_template=SimplePrintMessageTemplate)

    5.3. Create a subscription that connects the trigger and the backend. Add admin to the receiver(user) list.

    5.4. Run this command in manage.py shell:

    .. code-block:: python

        from django_signal_notifier.models import *
        TestModel1_another_instance = TestModel1.objects.create(name="new_test_model2", extra_field="extra")

    Now you should see a message when you create TestModel1. By Creating new TestModel1, Django calls the pre_save signal's send method. Then this signal call associated trigger handler.
    In the Trigger handler, the associated backend is called. The message_template with some details are sent to the backend.
    In our case, a simple message is printed. You can provide your messengers and message_templates.


.. |docs-badge| image:: https://img.shields.io/badge/docs-latest-informational.svg
   :target: `documentation`_
   :alt: Documentation

.. |pypi-badge| image:: https://img.shields.io/pypi/v/django_signal_notifier.svg
   :target: https://pypi.org/project/django-signal-notifier/
   :alt: Project on PyPI

.. _documentation: https://django-signal-notifier.readthedocs.io/
