import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Notification
from django.contrib.auth.models import User

print("=== NOTIFICATION CHECK ===")
print(f"Total notifications in database: {Notification.objects.count()}")
print(f"Unread notifications: {Notification.objects.filter(is_read=False).count()}")
print(f"Notifications about Test_admin: {Notification.objects.filter(message__contains='Test_admin').count()}")

print("\n=== SUPER ADMIN USERS ===")
super_admins = User.objects.filter(is_superuser=True, role__in=['super_admin', 'developer'])
for user in super_admins:
    notif_count = Notification.objects.filter(user=user).count()
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    print(f"{user.username} (role: {user.role}) - {notif_count} total, {unread_count} unread")

print("\n=== RECENT NOTIFICATIONS (Last 5) ===")
for notif in Notification.objects.order_by('-created_at')[:5]:
    print(f"[{notif.created_at}] {notif.user.username}: {notif.message[:50]}...")
