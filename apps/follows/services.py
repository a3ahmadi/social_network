from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from apps.accounts.models import Profile
from django.db import transaction
from django.db.models import F
from .models import Follow

User = get_user_model()

@transaction.atomic
def follow_user(user, target_user):

    if user == target_user:
        raise ValidationError("You cannot follow yourself.")

    _, created = Follow.objects.get_or_create(
        follower=user,
        following=target_user
    )

    if not created:
        return "already_following"

    Profile.objects.filter(
        user=user
    ).update(
        following_count=F('following_count') + 1
    )

    Profile.objects.filter(
        user=target_user
    ).update(
        followers_count=F('followers_count') + 1
    )

    return "followed"

@transaction.atomic
def unfollow_user(user, target_user):

    deleted, _ = Follow.objects.filter(
        follower=user,
        following=target_user
    ).delete()

    if not deleted:
        return "not_following"

    Profile.objects.filter(
        user=user
    ).update(
        following_count=F('following_count') - 1
    )

    Profile.objects.filter(
        user=target_user
    ).update(
        followers_count=F('followers_count') - 1
    )

    return "unfollowed"


def get_followers(user):
    return Follow.objects.filter(following=user)


def get_followings(user):
    return Follow.objects.filter(follower=user)