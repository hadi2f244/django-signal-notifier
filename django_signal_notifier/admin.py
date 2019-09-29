from django.contrib import admin
from django_signal_notifier.models import *
from django.apps import apps
from . import settings as app_settings

class TriggerAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        data = form.cleaned_data
        verb = data.get("verb")
        action_object_id = data.get("action_object_id")
        action_object_content_type = data.get("action_object_content_type")
        actor_object_content_type = data.get('actor_object_content_type')
        actor_object_id = data.get('actor_object_id')
        target = data.get("target")

        if action_object_id is None:
            action_object = action_object_content_type.model_class()
        else:
            if action_object_id != "":
                action_object = action_object_content_type.model_class().objects.filter(pk=int(action_object_id)).first()
            else:
                action_object = action_object_content_type.model_class()

        if actor_object_content_type is None:
            actor_object = None
        else:
            if actor_object_id != "":
                actor_object = actor_object_content_type.model_class().objects.filter(pk=int(actor_object_id)).first()
            else:
                actor_object = actor_object_content_type.model_class()
        print("action_object:",action_object)

        # Todo: If we edit a trigger what happens to the last item handler, Does it exits ?! remove it if necessary.
        Trigger.register_trigger(verb_name=verb, action_object=action_object, actor_object=actor_object, target=target)

admin.site.register(apps.get_model(app_settings.AUTH_USER_MODEL))
admin.site.register(Trigger, TriggerAdmin)
admin.site.register(Backend)
admin.site.register(Subscription)
admin.site.register(TestModel1)

