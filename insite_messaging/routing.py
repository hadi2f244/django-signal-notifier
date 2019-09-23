from django.conf.urls import url
from channels.routing import URLRouter
from channels.http import AsgiHandler
from channels.auth import AuthMiddlewareStack
import django_eventstream
from django.urls import include

urlpatterns = [
    url(r'^events/', AuthMiddlewareStack(
        URLRouter(django_eventstream.routing.urlpatterns)
    ), {'channels': ['test']}),
    url(r'^objects/(?P<user_id>\d+)/events/', AuthMiddlewareStack(
        URLRouter(django_eventstream.routing.urlpatterns)),
        {'format-channels': ['user_{user_id}']}),
    url(r'', AsgiHandler),
]
