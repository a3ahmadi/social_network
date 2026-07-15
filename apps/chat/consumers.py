from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.contrib.auth.models import User

from .models import Conversation, Message

import json


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        
        print("CONNECTED TO WEBSOCKET")

        self.conversation_id = self.scope[
            "url_route"
        ]["kwargs"]["conversation_id"]

        self.room_group_name = (
            f"chat_{self.conversation_id}"
        )

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):

        print(text_data)

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        text = data.get("text")

        if not text:
            return

        # فقط برای تست
        user = await database_sync_to_async(
            User.objects.get
        )(id=1)

        try:
            message = await self.create_message(
                user=user,
                text=text
            )
        except Conversation.DoesNotExist:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_id": message.id,
                "text": message.text,
                "sender": message.sender.username,
                "created_at": message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):

        print(event)

        await self.send(
            text_data=json.dumps(
                {
                    "id": event["message_id"],
                    "text": event["text"],
                    "sender": event["sender"],
                    "created_at": event["created_at"],
                }
            )
        )

    @database_sync_to_async
    def create_message(self, user, text):

        conversation = Conversation.objects.get(
            id=self.conversation_id
        )

        return Message.objects.create(
            conversation=conversation,
            sender=user,
            text=text
        )