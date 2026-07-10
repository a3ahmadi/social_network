from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


def get_story_expire_time():
    return timezone.now() + timedelta(hours=24)


class Story(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stories"
    )
    media = models.ImageField(
        upload_to="story_media"
    )
    expires_at = models.DateTimeField(
        default=get_story_expire_time
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.username
    
    class Meta:
        indexes = [
            models.Index(
                fields=["expires_at"]
            )
        ]



class StoryView(models.Model):
    user = models.ForeignKey(
        User,
        related_name='story_view',
        on_delete=models.CASCADE
    )
    story = models.ForeignKey(
        Story,
        related_name='story_view',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.user.username} -> {self.story.user.username}'
    
    class Meta:
        indexes = [
            models.Index(
                fields=["user", "story"]
            )
        ]
        unique_together = ('user', 'story')
