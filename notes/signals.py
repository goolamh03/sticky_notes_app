"""
Signal handlers for the Sticky Notes application.

This module contains Django signal receivers that perform
automatic actions when model events occur, such as creating
a profile when a new user account is created.
"""
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def ensure_profile(sender, instance, created, **kwargs):
    """Ensure that a user has an associated profile.

        Creates a new Profile when a user is created and guarantees that
        an existing user has a related Profile object if one does not
        already exist.

    Args:
        sender (Model): The model class sending the signal.
        instance (User): The user instance associated with the signal.
        created (bool): True if the user was newly created.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
