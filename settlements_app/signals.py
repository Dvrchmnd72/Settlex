from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_save_profile(sender, instance, created, **kwargs):
    """
    Creates a profile when a new user is created or saves the profile if it already exists.
    """
    if created:
        # If the user is created, create a new profile
        Profile.objects.create(user=instance)
    else:
        # If the user is updated, save the existing profile
        try:
            instance.profile.save()  # Save the profile if it exists
        except Profile.DoesNotExist:
            # In case the profile doesn't exist, create it
            Profile.objects.create(user=instance)

