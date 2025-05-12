from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    

    unread_notifications = notifications.filter(read=False)
    unread_notifications.update(read=True)
    
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

def notification_count(request):
    count = 0
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, read=False).count()
    return {'notification_count': count}


