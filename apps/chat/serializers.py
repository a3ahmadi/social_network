from rest_framework import serializers
from .models import Conversation, Message
from apps.accounts.models import Profile

class ConversationListSerializer(serializers.ModelSerializer):
    users = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="username"
    )
    last_message = serializers.SerializerMethodField()
    last_message_sender = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ("users", "is_group", "last_message", "last_message_sender")

    def get_last_message(self, obj):
        message = obj.messages.last()

        if message:
            return message.text

        return None
    
    def get_last_message_sender(self, obj):
        message = obj.messages.last()

        if message:
            return message.sender.username

        return None
    

class ConversationDetailSerializer(serializers.ModelSerializer):
    users = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="username"
    )
    class Meta:
        model = Conversation
        fields = ["id", "is_group", "created_at", "users"]


class ConversationMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username"
    )
    class Meta:
        model = Message
        fields = ["sender", "text", "is_read", "created_at"]


class UserListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username"
    )
    class Meta:
        model = Profile
        fields = ('username', 'name', 'avatar')


class ConversationSearchSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_sender = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            "user",
            "avatar",
            "is_group",
            "last_message",
            "last_message_sender",
        )

    def get_other_user(self, obj):
        request = self.context["request"]

        return obj.users.exclude(
            id=request.user.id
        ).first()

    def get_user(self, obj):
        user = self.get_other_user(obj)

        return user.username if user else None

    def get_avatar(self, obj):
        user = self.get_other_user(obj)

        if not user:
            return None

        profile = getattr(user, "profile", None)

        if profile and profile.avatar:
            return profile.avatar.url

        return None

    def get_last_message(self, obj):
        message = obj.messages.order_by("-created_at").first()

        return message.text if message else None

    def get_last_message_sender(self, obj):
        message = obj.messages.order_by("-created_at").first()

        return message.sender.username if message else None