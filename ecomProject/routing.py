from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import ecomApp.routing

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ecomApp.routing.websocket_urlpatterns
        )
    ),
})
