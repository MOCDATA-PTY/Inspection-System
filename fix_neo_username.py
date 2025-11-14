#!/usr/bin/env python3
"""
Script to change Neo's username to lowercase 'neo'
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
    print("FIXING NEO USERNAME")
    print("=" * 80)
    print()

    # Find the Neo user
    neo_user = User.objects.filter(username='Neo').first()

    if neo_user:
        print(f"Found user: {neo_user.username}")
        print(f"  Name: {neo_user.first_name} {neo_user.last_name}")
        print(f"  Email: {neo_user.email}")
        print()

        # Check if 'neo' already exists
        existing_neo = User.objects.filter(username='neo').first()
        if existing_neo:
            print("[ERROR] Username 'neo' already exists!")
            print(f"  Existing user: {existing_neo.first_name} {existing_neo.last_name}")
        else:
            # Change username to lowercase
            neo_user.username = 'neo'
            neo_user.save()
            print("[SUCCESS] Username changed from 'Neo' to 'neo'")
    else:
        print("[NOT FOUND] User 'Neo' not found")

    print()
    print("=" * 80)
