from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    caption = models.TextField(
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to="posts/"
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='likes',
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        related_name='posts',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.user.username} _ {self.post.caption}'
    
    class Meta:
        ordering = ('-created_at',)
        unique_together = ('user', 'post')


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name="repli",
        blank=True,
        null=True
    )
    text = models.CharField(
        max_length=500
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def clean(self):
        if self.parent and self.parent.post_id != self.post_id:
            raise ValidationError(
                "Parent comment must belong to the same post."
            )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["-created_at"]
