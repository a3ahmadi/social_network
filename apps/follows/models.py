from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )

    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def clean(self):
        if self.follower == self.following:
            raise ValidationError(
                "You cannot follow yourself."
            )

    def __str__(self):
        return f'{self.follower} follow {self.following}'
    
    class Meta:
        ordering = ('-created_at',)
        unique_together = ('follower', 'following')
        verbose_name = "Follow"
        verbose_name_plural = "Follows"
