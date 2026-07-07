from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from .models import Like, Post, SavedPost

User = get_user_model()

def like_post(user, post_id):
    post = get_object_or_404(Post, id=post_id)

    _, created = Like.objects.get_or_create(
        user=user,
        post=post
    )

    if created:
        return "liked"

    return "already_liked"


def unlike_post(user, post_id):
    deleted, _ = Like.objects.filter(
        user=user,
        post_id=post_id
    ).delete()

    if deleted:
        return "unliked"

    return "not_liked"


def post_likes_list(post_id):
    return Like.objects.filter(post_id=post_id)


def save_post(post_id, user):
    _,created = SavedPost.objects.get_or_create(
        post_id=post_id,
        user=user
    )

    if created:
        return "saved_post"
    
    return "post_already_saved"


def delete_saved_post(post_id, user):
    deleted, _ = SavedPost.objects.filter(
        post_id=post_id,
        user=user
    ).delete()

    if deleted:
        return "delete_saved_post"
    
    return "not_saved_post"