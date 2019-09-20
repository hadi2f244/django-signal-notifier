from django.urls import path, re_path
from .views import test_notifications, update_message_view

app_name = "insite_notifications"

urlpatterns = [
    path("test/", test_notifications, name="test"),
    path("update_message/", update_message_view, name="update_message_list_view"),
    re_path(r'update_message/(?P<user_id>\d+)/', update_message_view, name="update_message_list_view"),
]
