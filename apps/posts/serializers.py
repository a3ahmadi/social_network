from rest_framework import serializers
from .models import Post
from apps.accounts.models import Profile

class PostUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username"
    )
    class Meta:
        model = Profile
        fields = ('username', 'name', 'avatar')


class PostSerializer(serializers.ModelSerializer):
    user = PostUserSerializer(
        source="user.profile",
        read_only=True
    )
    class Meta:
        model = Post
        fields = "__all__"

