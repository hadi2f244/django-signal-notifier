from channels.routing import ProtocolTypeRouter, URLRouter
import insite_messaging.routing

application = ProtocolTypeRouter({
    'http': URLRouter(insite_messaging.routing.urlpatterns),
})
