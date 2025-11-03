#!/usr/bin/env python3
"""
Test script to display all users in the database
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if __name__ == '__main__':
    print("=" * 80)
    print("ALL USERS IN DATABASE")
    print("=" * 80)
    print()

    users = User.objects.all().order_by('id')

    if not users:
        print("No users found in database.")
    else:
        print(f"Total Users: {users.count()}")
        print()

        for i, user in enumerate(users, 1):
            print(f"{i}. User ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   First Name: {user.first_name}")
            print(f"   Last Name: {user.last_name}")

            # Check if user has role attribute
            if hasattr(user, 'role'):
                print(f"   Role: {user.role}")

            print(f"   Is Active: {user.is_active}")
            print(f"   Is Staff: {user.is_staff}")
            print(f"   Is Superuser: {user.is_superuser}")
            print(f"   Date Joined: {user.date_joined}")
            print(f"   Last Login: {user.last_login}")
            print()

    print("=" * 80)
