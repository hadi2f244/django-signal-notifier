from channels.routing import ProtocolTypeRouter, URLRouter
import insite_notifications.routing

application = ProtocolTypeRouter({
    'http': URLRouter(insite_notifications.routing.urlpatterns),
})
