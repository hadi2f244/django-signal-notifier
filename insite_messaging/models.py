import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django_eventstream import send_event
from django.db.models.signals import m2m_changed
from django.dispatch.dispatcher import receiver

# Create your models here.
from django_signal_notifier.messengers import BaseMessenger
from testDjango import settings


# User = get_user_model()

class UpdateMessages(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	user_id = models.IntegerField(blank=True)
	context = models.TextField()

	def delete(self, using=None, keep_parents=False):
		super(UpdateMessages, self).delete(using=using, keep_parents=keep_parents)
		count_update = UpdateMessages.objects.filter(user_id=self.user_id).count()
		send_event("user_%d" % self.user_id, "update", {'number': count_update})

	def save(self, *args, **kwargs):
		count_update = UpdateMessages.objects.filter(user_id=self.user_id).count()
		print(self.user_id, count_update)
		send_event("user_%d" % self.user_id, "update", {'number': count_update + 1})
		super(UpdateMessages, self).save(*args, **kwargs)

	def __str__(self):
		return "update messages for user %d and context %s ..." % (self.user_id, self.context[:10])


class Messages(models.Model):
	user_receivers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="UserMessages")
	# user_receivers = models.ManyToManyField(User, through="UserMessages", through_fields=('messages', 'user'))
	context = models.TextField(null=True)

# @receiver(m2m_changed, sender=Messages)
# def tets(sender, instance, **kwargs):
#     print(instance)
