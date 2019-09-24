from django.contrib import admin
from .models import *
from django.forms.models import ModelForm


# Register your models here.

class MessagesAdminForm(ModelForm):
	class Meta:
		model = Messages
		fields = "__all__"

	def clean(self):
		context = self.cleaned_data["context"]
		for user in self.cleaned_data["user_receivers"]:
			print("Update Message create for user id %d" % user.id)
			upmess = UpdateMessages(user_id=user.id, context=context)
			upmess.save()


class MessagesAdminModel(admin.ModelAdmin):
	model = Messages
	form = MessagesAdminForm


# admin.site.register(Messages)
admin.site.register(Messages, MessagesAdminModel)
admin.site.register(UpdateMessages)
# admin.site.register(UserMessages)
