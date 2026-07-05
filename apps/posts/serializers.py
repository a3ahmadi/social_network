from rest_framework import serializers
from .models import Post, Like
from apps.accounts.models import Profile

class UserListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username"
    )
    class Meta:
        model = Profile
        fields = ('username', 'name', 'avatar')


class PostSerializer(serializers.ModelSerializer):
    user = UserListSerializer(
        source="user.profile",
        read_only=True
    )
    class Meta:
        model = Post
        fields = "__all__"


class LikeListSerializer(serializers.ModelSerializer):
    user = UserListSerializer(
        source="user.profile",
        read_only=True
    )
    class Meta:
        model = Like
        fields = ('user',)
