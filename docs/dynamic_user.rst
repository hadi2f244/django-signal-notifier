============
Dynamic User
============

You can choose some users and groups as the receiver of the message in the subscription model.
Although there are many conditions that we want to set the receiver user dynamically.
First, let's take a look at a scenario. Then we present the solution to the problem.
Assume there are two models, ``Movie`` and ``User``.
We want to notify the audiences (``user``s) of a movie when it releases.

.. code-block:: python

    class Movie(models.Model):
        name = models.CharField(max_length=255)
        audiences = models.ManyToManyField(blank=True, to=User)

You probably defined a custom signal (e.g., *notify_audiences* ) that you call it(`send or send_rebust function <https://docs.djangoproject.com/en/3.0/topics/signals/#sending-signals>`_)
when you want to notify the audiences. So we don't discuss details of ``Trigger`` creation and the related process
that occurs in **DSN** anymore. (Refer to :doc:`introduction <introduction>` ).

The custom signal can be

.. code-block:: python

        notify_audiences = Signal(providing_args=["movie"])

*movie* parameter is used to pass the movie object.

To specify the dynamic user, A messenger must be designed as follows:

.. code-block:: python

    class Notify_audiences_messenger(BaseMessenger):
        @classmethod
        def send(self, template, users, trigger_context, signal_kwargs):
            # Ignore the messenger when movie was not specified.
            # We did it to avoid calling this messenger by other asymmetric signals other than notify_audiences
            try:
                movie = signal_kwargs['movie']
                audiences = movie.audiences
            except AttributeError:
                logger.error("Specified signal and Notify_audiences_messenger as backend don't match together.")
                return

            for user in audiences:
                message = template.render(user=user, trigger_context=trigger_context, signal_kwargs=signal_kwargs)

                # Send the rendered message to the user
                ...

As you see, the ``users`` argument(the set receivers in the subscription) is ignored, and a new user list is created. If you want to send the message to the preset receivers too, you can combine ``users`` and ``audiences``.

.. note::

    ``user`` parameter that template is rendered by, must be the type of ``AUTH_USER_MODEL`` (Refer to :doc:`settings <settings>`)

