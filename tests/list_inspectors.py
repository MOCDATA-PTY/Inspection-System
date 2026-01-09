#!/usr/bin/env python3
"""
Script to list all inspector accounts with their details
Note: This script cannot retrieve actual passwords as they are encrypted.
It will show a suggested password format instead.
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
    print("ALL INSPECTOR ACCOUNTS")
    print("=" * 80)
    print()

    inspectors = User.objects.filter(role='inspector').order_by('username')

    if not inspectors:
        print("No inspector accounts found.")
    else:
        print(f"Total Inspectors: {inspectors.count()}")
        print()

        for i, user in enumerate(inspectors, 1):
            print(f"{i}. Username: {user.username}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   Email: {user.email if user.email else 'Not set'}")

            # Show suggested password format
            if user.first_name and user.last_name:
                suggested_password = f"{user.first_name}{user.last_name}@2024"
            else:
                suggested_password = "[Password format: FirstLast@2024]"

            print(f"   Password: {suggested_password} (or contact admin)")
            print(f"   Last Login: {user.last_login if user.last_login else 'Never'}")
            print(f"   Date Joined: {user.date_joined}")
            print()

    print("=" * 80)
    print("NOTES:")
    print("=" * 80)
    print("- Passwords shown are in the format: FirstLast@2024")
    print("- If a user has changed their password, contact the admin for reset")
    print("- New accounts created today use the FirstLast@2024 format")
    print("=" * 80)
