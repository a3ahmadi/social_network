from rest_framework import serializers
from .models import Post, Like, Comment
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


class ReplySerializer(serializers.ModelSerializer):
    user = UserListSerializer(
        source="user.profile",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ("user", "text", "id")


class CommentListSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        required=False,
        allow_null=True
    )

    user = UserListSerializer(
        source="user.profile",
        read_only=True
    )

    replies = ReplySerializer(
        many=True,
        read_only=True,
        source="repli"
    )

    class Meta:
        model = Comment
        fields = (
            "user",
            "text",
            "id",
            "parent",
            "replies",
        )
        read_only_fields = (
            "user",
            "post",
            "parent",
            "created_at",
            "updated_at",
        )


class CommentDetailSerializer(serializers.ModelSerializer):
    user = UserListSerializer(
        source="user.profile",
        read_only=True
    )

    replies = ReplySerializer(
        many=True,
        read_only=True,
        source="repli"
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "text",
            "parent",
            "replies",
        )


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("text",)


class CommentCreateSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Comment
        fields = ("text", "parent")

    def validate_parent(self, value):
        post_id = self.context["view"].kwargs["post_id"]

        if value and value.post_id != post_id:
            raise serializers.ValidationError(
                "Parent comment must belong to the same post."
            )

        return value
    

class Feedserializer(serializers.Serializer):
    class Meta:
        model = Post
        fields = "__all__"