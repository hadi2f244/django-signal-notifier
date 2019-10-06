from django.contrib import admin
from .models import *
from django.forms.models import ModelForm


class MessagesModelAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'uuid', 'is_read', 'context']
    list_filter = ['user_receiver__last_login', 'is_read']

    def delete_queryset(self, request, queryset):
        for message in queryset:
            message.delete()

    class Meta:
        model = Messages


admin.site.register(Messages, MessagesModelAdmin)
