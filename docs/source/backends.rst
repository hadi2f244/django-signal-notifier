============
Backends
============

Each backend consists of two parts, messenger and message_template.
You can select them in admin panel, But if you want to define your own messenger or message_template you must define them before.


.. _Backends Custom_Message_template:

Custom Message_template
-----------------------
Each message_template is a class which inherits from BaseMessageTemplate class(###link to the class##). We have to dissect BaseMessageTemplate and explain some details.

* ``file_name`` and ``template_string`` :
    Each message_template has a string template based on `Django template language <https://docs.djangoproject.com/en/3.0/ref/templates/language/>`_. It can be a simple string, html or etc.
    You can set it directly by *template_string* variable or set a file by *file_name*. At first *DSN* checks *file_name* to get template string from it.
    Same as each Django app, template files are in **app_name/template/app_name**.
    So that, you must define that template file in the app that you defined new message_template class (You can refer to DSN_Notification ####links#### example for more details).
    .. code-block:: python

        file_name = "app_name/my_template.html"

    If *file_name* is leaved empty, *template_string* will be set as the template string.
    There is no preferences between these two way. Use whatever you prefer.

    An example:

    .. code-block:: python

            template_string = """
			{% if \"verb\" in context and context.verb != None %}
				<div>
					<p>{{ context.verb }}</p>
				</div>
			{% endif %} """

* ``render(self, user, trigger_context, signal_kwargs)`` :
    Messengers use this function to render template_message by the passed context.
    A Context is a dictionary which consists of three parts:

    * ``user``: The User object that the message_template should render for. We pass it to the message_template to access user's name. (e.g. The user's name can be set at the message header).
    * ``trigger_context``: It consists of :ref:`four trigger's parameters<Introduction Concepts Trigger>`.
    * ``signal_kwargs``: Other signal arguments that is passed to *DSN* can be accessed from this.


    .. note::

        You shouldn't change this function. We just explain it to show the how message_template class works. If you prefer to add more variable to the context change ``get_template_context`` function.

* ``get_template_context(self, context)`` :
    *User*, *trigger_context* and *signal_kwargs* are concatenated as *context*.
    You can any new variables to *context*. For instance, you can add time of message sending to the template context:

    .. code-block:: python

        def get_template_context(self, context):
            context['current_time'] = str(datetime.datetime.now().date())
            return context


    .. note::

        Notice that it doesn't call super class **get_template_context** method. So you should call parent's method manually in your code if you want:

            .. code-block:: python

                def get_template_context(self, context):
                    context = super().get_template_context(context)

                    # Your code :
                    ...

Briefly, You must set a template string or template_file for the message_template by ``file_name`` or ``template_string``.
To add more variables to the message context, You must overwrite ``get_template_context`` function.


.. _Backends Custom_Messenger:

Custom Messenger
-----------------
Like message_template, every messenger is a class which inherits from a base class named BaseMessenger(###link to the class##).
To define your own messenger, You must redefine **send()** class method.

``send(self, template, sender, users, trigger_context, signal_kwargs)``:

* ``template``: This is the template object.

* ``users``: List of users that you must send the message for them.

  Some messengers can send users's messages simultaneously to improve performance. Hence we avoid calling send function for each user singly.
  Instead we left it to the messenger to send messages to users.

* ``trigger_context``: Same as message_template

* ``signal_kwargs``: Same as message_template

First you must render the template class, by ``user``, ``trigger_context``, ``signal_kwargs``. You can render every user message by using a for loop over ``users`` list. Then you can send rendered string message to the user.
Example:

.. code-block:: python

    class simple_Messenger(BaseMessenger):
        @classmethod
        def send(self, template, users, trigger_context, signal_kwargs):
            for user in users:
                rendered_message = template.render(user=user, trigger_context=trigger_context, signal_kwargs=signal_kwargs)

                My_messenger.send_my_message(user_receiver=user, context=rendered_message)


.. note::

    For more details how to define a new message_template and messenger, refer to DSN_Notification ###link ##### documentation.


.. _Backends Add_message_template_and_messenger:

Add message_template and messenger
-------------------------------------
We suggest to define your messengers and message_templates in a separate file. E.g. messengers.py or message_template.py

You must introduce the new message_template and messenger to *DSN*. Use ``Add_Messenger`` and ``Add_Message_Template`` functions to add new messenger and message_template, respectively.
You must do it in ``ready()`` function in apps.py of your app.


.. code-block:: python

    from django_signal_notifier.message_templates import Add_Message_Template
    from django_signal_notifier.messengers import Add_Messenger

    class MyAppConfig(AppConfig):
        ...

        def ready(self):
            from myapp.messengers import simple_Messenger
            from myapp.message_templates import simple_Message_template

            ...

            # Messengers :
            Add_Messenger(simple_Messenger)
            # Message templates :
            Add_Message_Template(simple_Message_template)


.. attention::

    Because apps.py runs in migration. To avoid initialization problems
    You should import your own messenger and message_template classes in ready function.

After you rerun the app you can see your messengers and message_templates are added to messenger and message_template lists, respectively.
