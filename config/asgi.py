import os

from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter

from django.core.asgi import get_asgi_application

from apps.chat.routing import (
    websocket_urlpatterns as chat_ws
)

from apps.notifications.routing import (
    websocket_urlpatterns as notification_ws
)

from apps.chat.middleware import JwtAuthMiddleware

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)
django_asgi_app = get_asgi_application()

websocket_urlpatterns = (
    chat_ws +
    notification_ws
)

application = ProtocolTypeRouter({

    "http": django_asgi_app,

    "websocket": JwtAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})