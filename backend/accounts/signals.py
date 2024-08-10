from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import UserProfile


@receiver(post_save, sender=User)
def create_profile_for_user(sender, created, instance, **kwargs):
    """Create a profile for each user that's created."""
    if created:
        UserProfile.objects.create(user=instance)
