from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'active')
    list_filter = ('active', 'created_at')
    search_fields = ('title', 'message')
