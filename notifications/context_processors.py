# notifications/context_processors.py
from .models import Notification

def notifications_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(active=True).exclude(read_by=request.user).count()
    else:
        count = 0
    return {"notifications_count": count}
