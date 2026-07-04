from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from .models import Follow

User = get_user_model()


def follow_user(user, username):
    following = get_object_or_404(User, username=username)

    if user == following:
        raise ValidationError("You cannot follow yourself.")

    _, created = Follow.objects.get_or_create(
        follower=user,
        following=following
    )

    if not created:
        return "already_following"

    return "followed"


def unfollow_user(user, username):
    following = get_object_or_404(User, username=username)

    deleted, _ = Follow.objects.filter(
        follower=user,
        following=following
    ).delete()

    if not deleted:
        return "not_following"

    return "unfollowed"


def get_followers(user):
    return Follow.objects.filter(following=user)


def get_followings(user):
    return Follow.objects.filter(follower=user)