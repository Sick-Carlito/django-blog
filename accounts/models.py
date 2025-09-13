# accounts/models.py
# Profile model that extends the default User with avatar and bio.

from django.db import models                         # Django models
from django.conf import settings                     # to reference AUTH_USER_MODEL
from django.urls import reverse                       # optional helper for get_absolute_url


class Profile(models.Model):
    """
    Simple profile model attached OneToOne to the user.
    Fields:
      - user: OneToOneField to AUTH_USER_MODEL (user)
      - avatar: optional ImageField stored under MEDIA_ROOT/avatars/
      - bio: short free-text bio
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,                     # reference to the configured user model
        on_delete=models.CASCADE,                     # delete profile if user is deleted
        related_name="profile",                        # user.profile to access this
    )
    avatar = models.ImageField(
        upload_to="avatars/",                          # save under MEDIA_ROOT/avatars/
        null=True,                                     # allow no avatar
        blank=True,                                    # optional in forms
    )
    bio = models.TextField(
        blank=True,                                    # optional bio
        default="",                                    # default empty string
    )

    created_at = models.DateTimeField(auto_now_add=True)  # timestamp when created
    updated_at = models.DateTimeField(auto_now=True)      # timestamp when updated

    def __str__(self):
        """
        Human readable representation for admin and debugging.
        """
        return f"Profile for {self.user.username}"

    def get_avatar_url(self):
        """
        Helper: return avatar URL if set, else return placeholder or empty string.
        """
        if self.avatar:
            return self.avatar.url
        return ""
