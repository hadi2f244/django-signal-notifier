from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from django_signal_notifier.models import *


# class TriggerActionObjectFilter(admin.SimpleListFilter):
#     title = 'By action_object'
#
#     parameter_name = 'action_object_content_type'
#     def lookups(self, request, model_admin):


class SubscriptionInlineFormSet(BaseInlineFormSet):

    def clean(self):
        # Because there is a manytomany field(backends) in Subscription model,
        #   We can't check it in the model.clean function
        if self.instance.pk is None and len(self.forms) != 0:
            raise ValidationError(["You should save the trigger first then add subscriptions for it.",
                                   mark_safe("<a href='.''>Reload the page</a>")])
        for subscription_form in self.forms:
            Subscription.validate_subscription(subscription_form.instance, subscription_form.cleaned_data['trigger'],
                                               subscription_form.cleaned_data['backends'].all(), verbose=True)


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    formset = SubscriptionInlineFormSet
    extra = 0
    fields = ('enabled', 'backends', 'receiver_groups', 'receiver_users')


class ContentTypeModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # maybe you can find better solution to get app_label
        return "%s . %s" % (obj.app_label, obj)


class ListTextWidget(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list': 'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item
        data_list += '</datalist>'

        return text_html + data_list


class TriggerTemplateForm(forms.ModelForm):
    action_object_content_type = ContentTypeModelChoiceField(required=False,
                                                             queryset=ContentType.objects.all().order_by('app_label',
                                                                                                         'model'))
    actor_object_content_type = ContentTypeModelChoiceField(required=False,
                                                            queryset=ContentType.objects.all().order_by('app_label',
                                                                                                        'model'))
    verb = forms.CharField(
        widget=ListTextWidget(name=Trigger._meta.get_field('verb').verbose_name, data_list=django_default_signal_list))

    class Meta:
        model = Trigger
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            if kwargs['instance'] is not None:
                self.is_builtin_signal = kwargs['instance'].verb in django_default_signal_list


class TriggerAdmin(admin.ModelAdmin):
    form = TriggerTemplateForm
    inlines = (SubscriptionInline,)
    fieldsets = (
        (None, {
            'fields': ('enabled', 'verb', 'action_object_content_type', 'action_object_id')
        }),
        ("Extra fields", {
            'fields': ('actor_object_content_type', 'actor_object_id', 'target'),
            'classes': ('wide',)
        })
    )
    search_fields = ['verb']
    list_filter = ['verb']
    list_display = [
        'verb',
        'enabled',
        'action_object_content_type',
        'action_object_id',
        'actor_object_content_type',
        'actor_object_id',
        'target'
    ]

    def save_model(self, request, obj, form, change):
        data = form.cleaned_data
        verb = data.get("verb")
        enabled = data.get("enabled")
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
            Trigger.save_by_model(verb_name=verb, enabled=enabled, action_object=action_object,
                                  actor_object=actor_object,
                                  target=target, trigger_obj=obj)
        else:  # save_by_model will create new Trigger, too.
            Trigger.save_by_model(verb_name=verb, enabled=enabled, action_object=action_object,
                                  actor_object=actor_object,
                                  target=target)


class SubscriptionTemplateForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = "__all__"

    def clean(self):
        # Because there is a manytomany field(backends) in Subscription model,
        #   We can't check it in the model.clean function
        Subscription.validate_subscription(self.instance, self.cleaned_data['trigger'],
                                           self.cleaned_data['backends'].all())


class SubscriptionAdmin(admin.ModelAdmin):
    form = SubscriptionTemplateForm
    fieldsets = (
        (None, {
            'fields': ('enabled', 'trigger', 'backends')
        }),
        ("Set Receivers", {
            'fields': ('receiver_groups', 'receiver_users'),
            'classes': ('collapse',)
        })
    )
    list_filter = ['enabled']
    list_display = [
        'trigger',
        'enabled'
    ]

    def make_subscription_enabled(self, request, queryset):
        queryset.update(enabled=True)

    make_subscription_enabled.short_description = "Enable selected subscriptions"

    def make_subscription_disabled(self, request, queryset):
        queryset.update(enabled=False)

    make_subscription_disabled.short_description = "Disable selected subscriptions"

    actions = [make_subscription_enabled, make_subscription_disabled]


class BackendTemplateForm(forms.ModelForm):
    class Meta:
        model = Backend
        fields = "__all__"

    def clean(self):
        # Because there is a manytomany field(backends) in Subscription model,
        #   We can't check it in the model.clean function
        if self.instance.pk is not None:
            subscriptions = self.instance.subscription_set.all()
            modified_instance = Backend(**self.cleaned_data)
            for subscription in subscriptions:
                Subscription.validate_subscription(subscription, subscription.trigger,
                                                   [modified_instance], verbose=True)


class BackendAdmin(admin.ModelAdmin):
    form = BackendTemplateForm
    search_fields = ['messenger', 'message_template']
    list_filter = ['messenger']
    list_display = [
        'messenger',
        'message_template'
    ]



admin.site.register(Trigger, TriggerAdmin)
admin.site.register(Backend, BackendAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(DSN_Profile)
