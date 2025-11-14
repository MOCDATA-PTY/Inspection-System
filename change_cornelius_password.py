#!/usr/bin/env python3
"""
Script to change password for Cornelius Adams
"""
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def find_user():
    """Find the user by searching for variations of the name"""
    # Try different variations of the name
    search_terms = [
        'conelius',
        'cornelius',
        'admas',
        'adams',
    ]

    # Search by username
    for term in search_terms:
        users = User.objects.filter(username__icontains=term)
        if users.exists():
            return users.first()

    # Search by first_name or last_name
    for term in search_terms:
        users = User.objects.filter(first_name__icontains=term)
        if users.exists():
            return users.first()
        users = User.objects.filter(last_name__icontains=term)
        if users.exists():
            return users.first()

    return None

def change_password():
    """Change the password for Cornelius Adams"""

    print("\n" + "=" * 80)
    print("PASSWORD CHANGE FOR CORNELIUS ADAMS")
    print("=" * 80)

    # Find the user
    user = find_user()

    if not user:
        print("\nERROR: Could not find user 'Conelius admas' or similar variations.")
        print("\nSearching all users for reference:")
        all_users = User.objects.all()
        for u in all_users:
            print(f"  - Username: {u.username}, Name: {u.first_name} {u.last_name}")
        return

    print(f"\nUser found:")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email or 'N/A'}")
    print(f"  Full Name: {user.first_name} {user.last_name}")
    print(f"  Role: {getattr(user, 'role', 'N/A')}")

    # New password
    new_password = "Cornelius2025!"

    # Change the password
    user.set_password(new_password)
    user.save()

    print("\n" + "=" * 80)
    print("PASSWORD CHANGED SUCCESSFULLY!")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("NEW CREDENTIALS:")
    print("=" * 80)
    print(f"\nUsername: {user.username}")
    print(f"Password: {new_password}")
    print("\nPlease save these credentials in a secure location.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    try:
        change_password()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
