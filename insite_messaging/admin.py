from django.contrib import admin
from .models import *
from django.forms.models import ModelForm


class MessagesModelAdmin(admin.ModelAdmin):
	list_display = ['__str__', 'is_read', 'context']
	list_filter = ['user_receiver__last_login', 'is_read']

	class Meta:
		model = Messages


admin.site.register(Messages, MessagesModelAdmin)
