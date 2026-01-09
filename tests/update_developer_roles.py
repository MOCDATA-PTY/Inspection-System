"""
Update Ethan and developer users to have developer role
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 80)
print("UPDATING USER ROLES TO DEVELOPER")
print("=" * 80)

# Users to update
usernames_to_update = ['ethan', 'developer']

for username in usernames_to_update:
    try:
        user = User.objects.get(username=username)
        old_role = user.role if hasattr(user, 'role') else 'N/A'

        user.role = 'developer'
        user.save()

        print(f"\n[OK] Updated {username}:")
        print(f"     Old role: {old_role}")
        print(f"     New role: developer")

    except User.DoesNotExist:
        print(f"\n[ERROR] User '{username}' not found")
    except Exception as e:
        print(f"\n[ERROR] Failed to update {username}: {e}")

# Verify the changes
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

developers = User.objects.filter(role='developer').order_by('username')
print(f"\nUsers with 'developer' role: {developers.count()}")
print(f"\n{'Username':<20} {'Email':<35} {'Staff':<8} {'Superuser':<10}")
print("-" * 75)

for user in developers:
    username = user.username[:18]
    email = (user.email or 'N/A')[:33]
    is_staff = 'Yes' if user.is_staff else 'No'
    is_super = 'Yes' if user.is_superuser else 'No'
    print(f"{username:<20} {email:<35} {is_staff:<8} {is_super:<10}")

print("\n" + "=" * 80)
