from django.urls import path
from .consumers import ChatConsumer
from .conversation_consumers import (
    ConversationListConsumer
)

websocket_urlpatterns = [

    path(
        "ws/chat/<int:conversation_id>/",
        ChatConsumer.as_asgi()
    ),

    path(
        "ws/conversations/",
        ConversationListConsumer.as_asgi()
    ),
]