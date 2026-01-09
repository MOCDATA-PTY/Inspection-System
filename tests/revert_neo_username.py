#!/usr/bin/env python3
"""
Script to change neo's username back to 'Neo'
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
    print("REVERTING NEO USERNAME")
    print("=" * 80)
    print()

    # Find the neo user
    neo_user = User.objects.filter(username='neo').first()

    if neo_user:
        print(f"Found user: {neo_user.username}")
        print(f"  Name: {neo_user.first_name} {neo_user.last_name}")
        print(f"  Email: {neo_user.email}")
        print()

        # Change username back to Neo
        neo_user.username = 'Neo'
        neo_user.save()
        print("[SUCCESS] Username changed from 'neo' back to 'Neo'")
    else:
        print("[NOT FOUND] User 'neo' not found")

    print()
    print("=" * 80)
