from django.urls import path, re_path
from .views import test_notifications, update_message_view, messages_view

app_name = "insite_notifications"

urlpatterns = [
    path("test/", test_notifications, name="test"),
    path("update_message/", update_message_view, name="update_message_list_view"),
    re_path(r'update_message/(?P<user_id>\d+)/$', update_message_view, name="get_user_update_message"),
    re_path(r'update_message/(?P<user_id>\d+)/(?P<message_id>\d+)/$', update_message_view,
            name="delete_user_update_message"),
    re_path(r"messages/(?P<user_id>\d+)/$", messages_view, name="message_list_view"),
]
