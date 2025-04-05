from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@login_required
def messages_view(request):
    # Get the filter option from the query string; defaults to "all"
    filter_param = request.GET.get('filter', 'all')

    # Start with all active notifications
    all_notifications = Notification.objects.filter(active=True)
    
    # Compute the unread count from all notifications
    unread_count = all_notifications.exclude(read_by=request.user).count()  # Fix name

    # Filter notifications based on the filter parameter
    if filter_param == 'read':
        notifications = all_notifications.filter(read_by=request.user)
    elif filter_param == 'unread':
        notifications = all_notifications.exclude(read_by=request.user)
    else:
        notifications = all_notifications

    return render(request, "notifications/messages.html", {
        "notifications": notifications,
        "unread_count": unread_count,  # Fixed name
        "filter": filter_param,
    })

@login_required
def clear_notifications(request):
    if request.method == "POST":
        # Mark each active notification as read for the current user
        notifications = Notification.objects.filter(active=True)
        for note in notifications:
            note.read_by.add(request.user)
    return redirect("messages")




@login_required
@csrf_exempt
def mark_message_read(request, message_id):
    if request.method == "POST":
        try:
            message = Notification.objects.get(id=message_id)
            message.read_by.add(request.user)  # Mark message as read
            return JsonResponse({"status": "success"})
        except Notification.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Message not found"}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
