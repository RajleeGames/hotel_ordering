from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    # Provide a default value (an empty string) and allow null values.

    def __str__(self):
        return f"{self.user.username}'s Profile"
