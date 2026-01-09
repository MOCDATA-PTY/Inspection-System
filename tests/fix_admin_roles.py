"""
Fix admin user roles that got changed to inspector
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("FIXING ADMIN USER ROLES")
print("=" * 80)
print()

# Get all users
users = User.objects.all()

print(f"Total users: {users.count()}")
print()

print("Current user roles:")
print("-" * 80)
for user in users:
    role = getattr(user, 'role', 'N/A')
    print(f"Username: {user.username:20} | Superuser: {user.is_superuser} | Staff: {user.is_staff} | Role: {role}")

print()
print("-" * 80)
print("Fixing superuser roles...")
print("-" * 80)

# Fix all superusers
superusers = User.objects.filter(is_superuser=True)
for user in superusers:
    old_role = getattr(user, 'role', None)
    if hasattr(user, 'role'):
        user.role = 'administrator'
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"✓ Fixed {user.username}: {old_role} → administrator")

print()
print("=" * 80)
print("DONE - Admin roles have been restored")
print("=" * 80)
print()
print("Please restart Gunicorn:")
print("  sudo systemctl restart gunicorn")
