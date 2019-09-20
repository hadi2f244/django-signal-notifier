from django.db import models
from django_signal_notifier.models import BasicUser as User
from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from django_eventstream import send_event


# Create your models here.


class Messages(models.Model):
    user_receivers = models.ManyToManyField(User)
    # user_receivers = models.ManyToManyField(User, through="UserMessages", through_fields=('messages', 'user'))
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)


# class UserMessages(models.Model):
#     messages = models.ForeignKey(Messages, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#
#     def save(self, *args, **kwargs):
#         super(UserMessages, self).save(*args, **kwargs)
#         print(self)


# @receiver(post_save, sender=Messages)
def messages_post_save_handler(sender, instance, **kwargs):
    print(instance.user_receivers.all())
    # message_object = Messages.objects.get(id=instance.id)
    # print(message_object.user_receivers.all())
    # for user in message_object.user_receivers.all():
    #     update_message = UpdateMessages(user_id=user.id, title=message_object.title,
    #                                     description=message_object.description)
    #     update_message.save()


class UpdateMessages(models.Model):
    user_id = models.IntegerField(blank=True)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        super(UpdateMessages, self).save(*args, **kwargs)
        count_update = UpdateMessages.objects.filter(user_id=self.user_id).count()
        send_event("user_%d" % self.user_id, "update", {'number': count_update})
