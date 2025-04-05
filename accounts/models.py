# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"




User = get_user_model()

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        # Code expires in 15 minutes.
        return timezone.now() > self.created_at + timedelta(minutes=15)
    
    def __str__(self):
        return f"{self.user.email} - {self.code}"
