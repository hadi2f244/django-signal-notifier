=========================================
Introduction
=========================================

**DSN** or `django-signal-notifier <https://github.com/hadi2f244/django-signal-notifier>`_ is a Django app to send message or notification based on the Django's signals triggering. You can assign some backends to each signal(e.g. An In-Site notification app).

The major difference between ``django-signal-notifier`` and other Django's notification packages:

* ``django-signal-notifier`` is an ###

Concepts
========
**DSN** has 3 main parts:

* ``Trigger``
    Any django's signal can be connect to the corresponding trigger. There is an one-to-one connection between each signal and each trigger.

    Calling send method of the signal leads to calling the handler method of the corresponding trigger.

    Trigger has 4 parts(We got the idea from *Activity* concept in a similar package named `django-activity-stream <https://github.com/justquick/django-activity-stream>`_ ):

    * ``Actor``. The object that performed the activity.
    * ``Verb``. The verb phrase that identifies the action of the activity.
    * ``Action Object``. *(Optional)* The object linked to the action itself.
    * ``Target``. *(Optional)* The object to which the activity was performed.

    **Example**: A telegram client can be defined as a Backend for **DSN**.
    We can define a trigger that is connected to ``post_save`` signal and
    one of the project models(lets call it testmodel ) set as the action_object.
    So when we create new testmodel in anyplace###, the handler of the corresponding trigger is called automatically.

* ``Backend``
    Backend is a tool to send message like Notification, Email message or So on that is the main goal of **DSN**.
    We've got this idea from `django-sitemessage <https://github.com/idlesign/django-sitemessage>`_ ):
    Backend consists of **two** parts:

    1. ``Message_template``. It's a class as template of the message that contains a string or point to a template file.
    2. ``Messenger``. It's operational core of each backend that send the string message (rendered message_template). E.g. Telegram and email Client.

    **Example**: A telegram client can be defined as a Backend for **DSN**.

* ``Subscription``
    Triggers and Backends are connected in subscription entity.
    Message receivers are set in the subscription, too.

    If the handler method of a trigger is called, the related subscriptions receivers and backends are invoked.
    Then the backends(messenger) are called for each receiver(user). That's the main part of **DSN**.

    **Example**: Same as the above example, A trigger that is connected to the post_save for testmodel is defined.
    Also we have connected a subscription that set email messenger as the backend and Admin user as the receiver.
    Hence, If a new testmodel object is created, An email message is sent to the Admin.

    We can connect more than one subscription to a trigger. Subscriptions can be switched off.

    **Note**: You can send the message to a dynamic user(that changed according to the occasions) and
    receivers field are just provided in subscription for that situations that the receivers are static(e.g. sending some logs or notifications to Administrator user or group users).

Architecture
============

**DSN**'s architecture :

.. image:: images/DSN_Architecture.png
    :alt: DSN Architecture

As stated above, **DSN** consists 3 models(Trigger, Subscription and Backend).
**DSN** works as follow:
    1. **Setup** and **Initialization** steps:
        1.1. Custom messengers, message_templates and signals must be defined(*Optional*). It must be done through the code.
        1.2. 3 steps must be done through the admin panel:
            1.2.1. Triggers must be defined by the name of pre-defined signal(verb_name).

            1.2.2. Required backends must be defined by proper messenger and message_template.

            1.2.3. Subscription are the relations between the Trigger and Backends. So according to the logic of our code, We must select proper backends for a trigger in subscription.

    2. **Execution**: The code of **DSN** starts when a signal triggers(The send function calling).
        2.1. After the signal triggers, the handler method of the associated trigger will be called and It's check that passed signal arguments match the associated trigger.

        2.2. If every things match, associated subscription is evoked and a list of backends and receiver users are created.

        2.3. After that, each backend's messengers are called for the specified message and the user.
        (Note: We can set user dynamically. Hence associated user must be defined in the messenger and the receiver field in subscription must be leaved empty)

Summary
=======
    In nutshell, we can say **DSN** is developed to *send message* :

    * **When and Where** ? : When a Trigger Triggered (The related signal's send function is called and the trigger's specs match).
    * **What** to send?: The message that is created to the message_template and other parameters like signal_kwargs.
    * **Whom** to send? : Send the message to the registered receivers in the subscription or the dynamic user that can be specified in the messenger.

*Note*: You should pay attention to these 3 questions, When you want to assign a new trigger to a signal.
