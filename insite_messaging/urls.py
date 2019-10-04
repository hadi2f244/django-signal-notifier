from django.urls import path, re_path
from .views import test_notifications, messages_view, unread_messages_view

app_name = "insite_notifications"

urlpatterns = [
	path("test/", test_notifications, name="test"),
	re_path(r'messages/(?P<message_id>[A-Za-z0-9-]+)/$', unread_messages_view, name='seen_user_messages'),
	path('messages/unread/', unread_messages_view, name="get_user_new_message_list"),
	path('messages/', messages_view, name="get_user_all_messages")
	# re_path(r"messages/(?P<user_id>\d+)/$", messages_view, name="message_list_view"),
]
