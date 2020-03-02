============
Usage
============


.. _Usage Initialization:

Initialization
---------------
As stated in Architecture :ref:`Introduction Architecture` part of :doc:`Introduction <introduction>`, First You should implement a **trigger**
regarding these parameters:

* ``verb_name``: equals to the signal's name (*required*)
* ``action_object``: An object or a class model that the signal operated on it. It is exactly equal to **sender** parameter in signals. (*It's required for the pre-defined Django signals*)
* ``actor_object``: If you use a custom signal that you pass this parameter, you can use it (*Optional*)
* ``target``: It's just a simple string and used as a piece of side information. Same as *actor_object*, *target* is used with a custom signal (*Optional*).


Then you can define some **backend** s. We have already defined some messengers and message_templates
that are initialized on *DSN*'s core by default. You can implement your messengers and message_templates.
It's explained in :doc:`Backends <backends>`.

For connecting backend to the trigger, you must define at least one **subscription** and select the user and group
that must receive the message.


.. _Usage CustomSignal:

Custom Signal
--------------
In addition to django default signal(that we load all of them in **DSN** by default.), You can define your signal according to the `Django official documentation <https://docs.djangoproject.com/en/3.0/topics/signals/#defining-signals>`_. It's a standard way to define
custom signals in the `signals.py` of each app.

.. code-block:: python

    custom_signal = Signal(providing_args=["parameter1"])

Then you must set up the custom signal in the *ready* function of the app's config in `apps.py`:

.. code-block:: python


    class MyAppConfig(AppConfig):
        name = 'myapp'
        ...
        def ready(self):
           from .signals import custom_signal
           from django_signal_notifier.models import Trigger
           ...
           Trigger.registered_verb_signal('custom_signal', custom_signal)

.. attention::

    Because *apps.py* runs in migration too. To avoid initialization problems
    You **must** import django_signal_notifier and signals in ready function.

If you want to use **actor_object** or **target**, You must set them as the signal parameters.
**action_object** is optional, but it isn't necessary to be defined as a parameter, You can set it as signal **sender** parameters(Refer to Django signal documentation, ` *send* method part <https://docs.djangoproject.com/en/3.0/topics/signals/#django.dispatch.Signal.send_robust>`_)

.. note::

    **sender** is necessary for all pre-defined Django's signals. Therefore, *DSN* uses **sender** as **action_object** by default.

Same as a standard Django signal, you can use **send** and **send_robust** to trigger the signal.

