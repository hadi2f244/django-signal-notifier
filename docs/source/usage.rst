============
Usage
============

Initialization
---------------
As mentioned in Architecture part of Introduction (### Link###), First You should implement a **trigger**
considering these parameters:

* ``verb_name``: equals to the signal's name (*required*)
* ``action_object``: set object that the signal operated on. It is exactly equal to **sender** parameter in signals.(*It's required for the pre-defined django signals*)
* ``actor_object``: If you use a custom signal that you pass this parameter, you can use it (*Optional*)
* ``target``: It's just a simple string that is used as side description. Same as actor_object, It's used with a custom signal (*Optional*).


Then you should define some **backend**s, We defined some messenger and message_template
that are introduced to *DSN*'s core by default. You can implement your own that we explain
how to define in ### ###.

For connecting backend to the trigger, you must define at least one **subscription** and select the user and group
that must receive the message.

Custom Signal
--------------
In addition to django default signal(that we load all of them in **DSN** by default.), You can define your own signal according to the official Django document. It's standard way to define
custom signals in the `signals.py` of each app.

.. code-block:: python

    custom_signal = Signal(providing_args=["parameter1"])

Then you must setup the custom signal in the ready function of the app's config in `apps.py`:

.. code-block:: python


    class MyAppConfig(AppConfig):
        name = 'myapp'
        ...
        def ready(self):
           from .signals import custom_signal
           from django_signal_notifier.models import Trigger
           ...
           Trigger.init_verb_signal('custom_signal', custom_signal)

**Important**: Because appss.py runs in migration too.To avoid initialization problems
You **must** import django_signal_notifier and signals in ready function.

If you want to use **actor_object** or **target**, You must define them as the signal parameters.
**action_object** is optional, But it doesn't need to defined as a parameters, You can set it as signal **sender** parameters(Refer to django documentation####)

Same as a normal django signal you can use **send** and **send_robust** to trigger the signal.

