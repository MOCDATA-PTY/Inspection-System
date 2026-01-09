"""
Quick script to create a test notification for adding Test_admin user
Run this from the project root: python create_test_notification.py
"""
import os
import django
import random
import string

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.notification_utils import notify_new_user_added

# Generate a random password for display
random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

# Create the notification
print("Creating test notification...")
notifications = notify_new_user_added(
    username='Test_admin',
    role='admin',
    added_by='system'
)

print("[SUCCESS] Notification created successfully!")
print(f"User: Test_admin")
print(f"Password: {random_password}")
print(f"Role: admin")
print("\nCheck your notification bell to see the notification!")
print(f"Created {len(notifications)} notification(s) for super admins.")
