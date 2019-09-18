from django.db import models
from django_signal_notifier.models import BasicUser as User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django_eventstream import send_event


# Create your models here.

class Messages(models.Model):
    user_receivers = models.ManyToManyField(User)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)


@receiver(post_save, sender=Messages)
def messages_post_save_handler(sender, instance, **kwargs):
    print(instance.user_receivers.all())


class UpdateMessages(models.Model):
    user_id = models.IntegerField(blank=True)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        super(UpdateMessages, self).save(*args, **kwargs)
        count_update = UpdateMessages.objects.filter(user_id=self.user_id).count()
        send_event("user_%d" % self.user_id, "update", {'number': count_update + 1})
