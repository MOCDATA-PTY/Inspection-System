#!/usr/bin/env python3
"""
Script to fix usernames to only use part before first dot in email
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
    print("FIXING USERNAMES")
    print("=" * 80)
    print()

    # Users to fix
    fixes = [
        ('Corneliusadams', 'Cornelius', 'cornelius.adams@afsq.co.za'),
        ('Dimakatsomodiba', 'Dimakatso', 'dimakatso.modiba@afsq.co.za'),
    ]

    for old_username, new_username, email in fixes:
        user = User.objects.filter(username=old_username).first()

        if user:
            # Check if new username already exists
            existing = User.objects.filter(username=new_username).exclude(id=user.id).first()
            if existing:
                print(f"[ERROR] Cannot change '{old_username}' to '{new_username}' - username already exists")
            else:
                user.username = new_username
                user.save()
                print(f"[FIXED] {old_username} -> {new_username}")
                print(f"  Email: {email}")
        else:
            print(f"[NOT FOUND] User '{old_username}' not found")
        print()

    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)
