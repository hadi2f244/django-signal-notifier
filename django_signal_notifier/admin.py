from django.contrib import admin
from django_signal_notifier.models import *


class TriggerAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        data = form.cleaned_data
        verb = data.get("verb")
        action_object_id = data.get("action_object_id")
        action_object_content_type = data.get("action_object_content_type")
        actor_object_content_type = data.get('actor_object_content_type')
        actor_object_id = data.get('actor_object_id')
        target = data.get("target")

        if action_object_content_type is not None:
            if action_object_id is None or action_object_id == "":
                action_object = action_object_content_type.model_class()
            else:
                action_object = action_object_content_type.model_class().objects.get(
                    pk=int(action_object_id))
        else:
            action_object = None

        if actor_object_content_type is not None:
            if actor_object_id is None or actor_object_id == "":
                actor_object = actor_object_content_type.model_class()
            else:
                actor_object = actor_object_content_type.model_class().objects.get(
                    pk=int(actor_object_id))
        else:
            actor_object = None

        if obj.pk is not None:  # register trigger according to the previous object
            Trigger.register_trigger(verb_name=verb, action_object=action_object, actor_object=actor_object,
                                     target=target, trigger_obj=obj)
        else:  # register_trigger will create new Trigger, too.
            Trigger.register_trigger(verb_name=verb, action_object=action_object, actor_object=actor_object,
                                     target=target)


admin.site.register(Trigger, TriggerAdmin)
admin.site.register(Backend)
admin.site.register(Subscription)
admin.site.register(DSN_Profile)
