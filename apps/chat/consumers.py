from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Conversation, Message

import json


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.conversation_id = self.scope[
            "url_route"
        ]["kwargs"]["conversation_id"]

        is_member = await self.is_conversation_member()

        if not is_member:
            await self.close()
            return

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

        try:
            data = json.loads(text_data)

        except json.JSONDecodeError:
            return

        message_type = data.get("type")

        if message_type == "mark_read":

            await self.mark_messages_read()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "messages_read",
                    "reader": self.user.username,
                }
            )

            return

        text = data.get("text", "").strip()

        if not text:
            return

        try:

            message = await self.create_message(
                user=self.user,
                text=text
            )

        except Conversation.DoesNotExist:

            await self.close()
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_id": message.id,
                "text": message.text,
                "sender": message.sender.username,
                "created_at": (
                    message.created_at.isoformat()
                ),
            }
        )

    async def chat_message(self, event):

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

    async def messages_read(self, event):

        await self.send(
            text_data=json.dumps(
                {
                    "type": "messages_read",
                    "reader": event["reader"],
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

    @database_sync_to_async
    def is_conversation_member(self):

        return Conversation.objects.filter(
            id=self.conversation_id,
            users=self.user
        ).exists()
    
    @database_sync_to_async
    def mark_messages_read(self):

        Message.objects.filter(
            conversation_id=self.conversation_id,
            is_read=False
        ).exclude(
            sender=self.user
        ).update(
            is_read=True
        )