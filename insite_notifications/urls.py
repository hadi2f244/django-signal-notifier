from django.urls import path
from .views import test_notifications

app_name = "insite_notifications"

urlpatterns = [
    path("test/", test_notifications, name="test")
]
