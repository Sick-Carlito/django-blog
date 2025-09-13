# accounts/signals.py
# Signal handlers for the accounts app: auto-create Profile on User creation.

from django.db.models.signals import post_save     # signal that fires after model.save()
from django.dispatch import receiver                # decorator to connect signal handlers
from django.conf import settings                    # to get the user model
from .models import Profile                         # the Profile model

User = settings.AUTH_USER_MODEL                     # string reference or actual model depending on settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """
    When a new User is created, automatically create a linked Profile.
    - 'created' is True on first save() (user creation).
    """
    if created:
        # create Profile if it doesn't exist already
        Profile.objects.create(user=instance)