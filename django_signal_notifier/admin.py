from django.contrib import admin

from django_signal_notifier import models

admin.site.register(models.Subscription)
admin.site.register(models.Trigger)
admin.site.register(models.Backend)
