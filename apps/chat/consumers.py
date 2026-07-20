from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message
import json
from django.utils import timezone


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

        await self.set_online()

        self.room_group_name = (
            f"chat_{self.conversation_id}"
        )

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.set_offline()

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
        
        if message_type == "typing":

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_typing",
                    "username": self.user.username,
                }
            )
            return
        
        if message_type == "stop_typing":

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_stop_typing",
                    "username": self.user.username,
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

        user_ids = await (
            self.get_conversation_users()
        )

        for user_id in user_ids:

            await self.channel_layer.group_send(
                f"conversations_{user_id}",
                {
                    "type":
                        "conversation_update",

                    "conversation_id":
                        self.conversation_id,

                    "last_message":
                        message.text,

                    "sender":
                        self.user.username,

                    "created_at":
                        message.created_at.isoformat(),
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

    async def user_typing(self, event):

        if event["username"] == self.user.username:
            return

        await self.send(
            text_data=json.dumps(
                {
                    "type": "typing",
                    "user": event["username"],
                }
            )
        )

    async def user_stop_typing(self, event):

        if event["username"] == self.user.username:
            return

        await self.send(
            text_data=json.dumps(
                {
                    "type": "stop_typing",
                    "user": event["username"],
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

    @database_sync_to_async
    def set_online(self):

        profile = self.user.profile

        profile.is_online = True

        profile.save(
            update_fields=["is_online"]
        )

    @database_sync_to_async
    def set_offline(self):

        profile = self.user.profile

        profile.is_online = False
        profile.last_seen = timezone.now()

        profile.save(
            update_fields=[
                "is_online",
                "last_seen"
            ]
        )

    @database_sync_to_async
    def get_conversation_users(self):

        conversation = Conversation.objects.get(
            id=self.conversation_id
        )

        return list(
            conversation.users.values_list(
                "id",
                flat=True
            )
        )