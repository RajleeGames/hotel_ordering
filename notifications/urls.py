from django.urls import path
from .views import messages_view, clear_notifications, mark_message_read

urlpatterns = [
    path("messages/", messages_view, name="messages"),
    path("notifications/mark-read/<int:message_id>/", mark_message_read, name="mark_message_read"),
    path("clear-notifications/", clear_notifications, name="clear_notifications"),
]
