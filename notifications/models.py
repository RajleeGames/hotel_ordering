from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    # Track which users have read this notification
    read_by = models.ManyToManyField(User, blank=True, related_name="read_notifications")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
