from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    email = models.EmailField(
        null=True, blank=True
    )
    
    avatar = models.ImageField(
        upload_to='profile_avatar',
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    
    biography = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )
    
    website = models.URLField(
        null=True,
        blank=True
    )
    
    is_private = models.BooleanField(
        default=False
    )
    
    followers_count = models.PositiveBigIntegerField(
        default=0
    )
    
    following_count = models.PositiveBigIntegerField(
        default=0
    )
    
    posts_count = models.PositiveBigIntegerField(
        default=0
    )
    
    is_owner = models.BooleanField(
        default=False
    )

    is_online = models.BooleanField(
    default=False
    )

    last_seen = models.DateTimeField(
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    def __str__(self):
        return self.user.username
    
    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    
        



