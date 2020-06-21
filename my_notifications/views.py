from notifications.models import Notification
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect


def my_notifications(request):
    data = {}
    return render(request, 'my_notifications/my_notifications.html', context=data)


def my_notification(request, my_notification_pk):
    my_notification = get_object_or_404(Notification, pk=my_notification_pk)
    my_notification.unread = False
    my_notification.save()
    return redirect(my_notification.data['url'])


def delete_my_read_notifications(request):
    notifications = request.user.notifications.read()
    notifications.delete()
    return redirect(reverse('my_notifications:my_notifications'))