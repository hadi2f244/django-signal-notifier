import uuid

from django.db import models
from django_eventstream import send_event
from testDjango import settings


class Messages(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False, unique=True, verbose_name="ID",
	                      auto_created=True, serialize=False)
	user_receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="UserMessages", on_delete=models.CASCADE)
	is_read = models.BooleanField(default=False, blank=True)
	context = models.TextField(null=True, blank=True)

	def save(self, *args, **kwargs):
		super(Messages, self).save(*args, **kwargs)
		count_update = Messages.objects.filter(is_read=False).count()
		print(self.user_receiver_id, count_update)
		send_event("user_%d" % self.user_receiver_id, "update", {"number": count_update})

	def __str__(self):
		return "Message for user " + self.user_receiver.username + " : " + self.context[0:20]
