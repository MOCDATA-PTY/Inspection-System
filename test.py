#!/usr/bin/env python3
"""
Test script to find and display all users in the database
"""
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# Import User model after Django setup
from django.contrib.auth.models import User

def display_user(user, index, total):
    """Display a single user in a readable format"""
    print(f"\n[{index}/{total}]")
    print("=" * 80)
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email or 'N/A'}")
    print(f"Full Name: {user.first_name} {user.last_name}".strip() or 'N/A')

    # Custom fields
    print(f"Role: {getattr(user, 'role', 'N/A')}")
    print(f"Phone Number: {getattr(user, 'phone_number', 'N/A') or 'N/A'}")
    print(f"Department: {getattr(user, 'department', 'N/A') or 'N/A'}")
    print(f"Employee ID: {getattr(user, 'employee_id', 'N/A') or 'N/A'}")

    # Permissions
    print(f"\nPermissions:")
    print(f"  Active: {'Yes' if user.is_active else 'No'}")
    print(f"  Staff: {'Yes' if user.is_staff else 'No'}")
    print(f"  Superuser: {'Yes' if user.is_superuser else 'No'}")

    # Activity
    print(f"\nActivity:")
    print(f"  Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}")
    print(f"  Date Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def main():
    """Main function to find and display all users"""

    print("\n" + "=" * 80)
    print("USER DATABASE TEST - ALL USERS")
    print("=" * 80)

    # Get all users
    users = User.objects.all().order_by('id')
    total_count = users.count()

    print(f"\nTotal Users: {total_count}")

    if total_count == 0:
        print("\nNo users found in the database.")
        return

    # Display all users
    print("\n" + "-" * 80)
    print("USER LIST:")
    print("-" * 80)

    for idx, user in enumerate(users, 1):
        display_user(user, idx, total_count)

    # Statistics
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)

    # Count by role
    roles = User.objects.values_list('role', flat=True).distinct()
    print("\nUsers by Role:")
    for role in roles:
        if role:
            count = User.objects.filter(role=role).count()
            print(f"  {role}: {count}")

    # Count by status
    active_count = User.objects.filter(is_active=True).count()
    inactive_count = User.objects.filter(is_active=False).count()
    print(f"\nUsers by Status:")
    print(f"  Active: {active_count}")
    print(f"  Inactive: {inactive_count}")

    # Count by permissions
    staff_count = User.objects.filter(is_staff=True).count()
    superuser_count = User.objects.filter(is_superuser=True).count()
    print(f"\nUsers by Permissions:")
    print(f"  Staff: {staff_count}")
    print(f"  Superuser: {superuser_count}")

    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
