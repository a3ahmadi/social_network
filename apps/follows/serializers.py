from rest_framework import serializers
from .models import Follow


class FollowerListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    is_following_her = serializers.SerializerMethodField()
    class Meta:
        model = Follow
        fields = "name", "username", "avatar", "is_following_her"

    def get_name(self, obj):
        return obj.follower.profile.name
    
    def get_username(self, obj):
        return obj.follower.username
    
    def get_avatar(self, obj):
        return obj.follower.profile.avatar.url
    
    def get_is_following_her(self, obj):
        return Follow.objects.filter(
            follower=obj.following,
            following=obj.follower
        ).exists()
    

class FollowingListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    is_following_her = serializers.SerializerMethodField()
    class Meta:
        model = Follow
        fields = "name", "username", "avatar", "is_following_her"

    def get_name(self, obj):
        return obj.following.profile.name
    
    def get_username(self, obj):
        return obj.following.username
    
    def get_avatar(self, obj):
        return obj.following.profile.avatar.url
    
    def get_is_following_her(self, obj):
        return True