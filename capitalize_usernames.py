#!/usr/bin/env python3
"""
Script to capitalize the first letter of all inspector usernames
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
    print("CAPITALIZING INSPECTOR USERNAMES")
    print("=" * 80)
    print()

    inspectors = User.objects.filter(role='inspector').order_by('username')

    updated_count = 0
    skipped_count = 0

    for inspector in inspectors:
        old_username = inspector.username
        new_username = old_username[0].upper() + old_username[1:] if old_username else old_username

        if old_username != new_username:
            # Check if new username already exists
            existing = User.objects.filter(username=new_username).exclude(id=inspector.id).first()
            if existing:
                print(f"[SKIP] Cannot change '{old_username}' to '{new_username}' - username already exists")
                skipped_count += 1
            else:
                inspector.username = new_username
                inspector.save()
                print(f"[UPDATED] {old_username} -> {new_username}")
                updated_count += 1
        else:
            print(f"[OK] {old_username} already capitalized")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total inspectors: {inspectors.count()}")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {skipped_count}")
    print("=" * 80)
