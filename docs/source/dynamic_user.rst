============
Dynamic User
============

You can select some users and groups as receiver of the message in the subscription model.

Although there are many situations that we want to set receiver user dynamically.
First let's take a look at a scenario, Then we will provide the solution for the problem.

Suppose there are two models, ``Movie`` and ``User``.
We want to inform the audiences (``user``s) of the a movie when it releases.

.. code-block:: python

    class Movie(models.Model):
        name = models.CharField(max_length=255)
        audiences = models.ManyToManyField(blank=True, to=User)

You probably defined a custom signal (e.g. *inform_audiences* ) that you call it(`send or send_rebust function <https://docs.djangoproject.com/en/3.0/topics/signals/#sending-signals>`_)
when you want to inform the audiences. So we don't discuss about details of ``Trigger`` creation and the related process
that occurs in **DSN** anymore. (Refer to :doc:`introduction <introduction>` ).

The custom signal can be

.. code-block:: python

        inform_audiences = Signal(providing_args=["movie"])

So that we should use movie parameter to pass the movie object.

To specify the dynamic user, A messenger must be designed as follows:

.. code-block:: python

    class Inform_audiences(BaseMessenger):
        @classmethod
        def send(self, template, users, trigger_context, signal_kwargs):
            # Ignore the messenger when movie was not specified.
            # We did it to avoid calling this messenger by other asymmetric signals other than inform_audiences
            try:
                movie = signal_kwargs['movie']
                audiences = movie.audiences
            except AttributeError:
                print("Error: Specified signal and Inform_audiences as backend don't match together.")
                return

            for user in audiences:
                message = template.render(user=user, trigger_context=trigger_context, signal_kwargs=signal_kwargs)

                # Send the rendered message to the user
                ...

As you see, the ``users`` arguments is ignored and new users list is created. So according to above code, the set receivers in the subscription
are ignored. If you want to send the message to the preset receivers, you can combine ``users`` and ``audiences``.

.. note::

    ``user`` parameter that template is rendered by, must be type of ``AUTH_USER_MODEL`` (Refer to :doc:`settings <settings>`)

