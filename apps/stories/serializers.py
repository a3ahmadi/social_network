from rest_framework import serializers
from .models import Story
from django.contrib.auth import get_user_model

User = get_user_model()

class StoryUserSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(
        source="profile.avatar"
    )
    class Meta:
        model = User
        fields = ("avatar", "username")

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = "__all__"
        read_only_fields = (
            "user",
            "created_at",
            "expires_at",
        )


class StoryFeedSerializer(serializers.ModelSerializer):
    stories = StorySerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "stories",
        )
