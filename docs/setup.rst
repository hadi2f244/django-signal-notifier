

.. _Setup:

============
Setup
============


.. _Setup Requirements:

Requirements
------------

- Python 2.7, 3.4, 3.5, 3.6, 3.7
- Django 1.7, 1.8, 1.9, 1.10, 1.11, 2.0, 2.1, 2.2, 3.0

.. attention::
    django-signal-notifier==0.2.1 is not compatible with **django>=3.1** . We are solving the problem.


.. _Setup Installation:

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
