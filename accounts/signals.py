# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Auto-create or update Profile whenever User is created or saved."""
    if created:
        print(f"Creating profile for {instance.username}")
        Profile.objects.create(user=instance)
    else:
        print(f"Updating profile for {instance.username}")
    # Always save the profile
    instance.profile.save()
