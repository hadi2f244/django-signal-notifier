=====
DSN
=====

DSN or django_signal_notifier is a Django app to send message or notification based on a signal triggering. You can assign some backends to each signal(e.g. An In-Site message app)

Quick start
-----------

1. Add "django_signal_notifier" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django_signal_notifier',
    ]

2. Run `python manage.py migrate` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
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
