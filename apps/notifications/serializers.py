from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification
from apps.accounts.models import Profile

User = get_user_model()


class NotificationActorSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(
        source="profile.avatar"
    )
    class Meta:
        model = User
        fields = ("avatar", "username")


class NotificationSerializer(serializers.ModelSerializer):
    actor = NotificationActorSerializer()
    class Meta:
        model = Notification
        fields = ("id", "notification_type", "is_read", "created_at", "actor")