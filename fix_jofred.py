#!/usr/bin/env python3
"""
Script to fix Jofredsteyn to Jofred
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
    print("FIXING JOFRED USERNAME")
    print("=" * 80)
    print()

    user = User.objects.filter(username='Jofredsteyn').first()

    if user:
        # Check if new username already exists
        existing = User.objects.filter(username='Jofred').exclude(id=user.id).first()
        if existing:
            print(f"[ERROR] Cannot change - username 'Jofred' already exists")
        else:
            user.username = 'Jofred'
            user.save()
            print(f"[FIXED] Jofredsteyn -> Jofred")
    else:
        print(f"[NOT FOUND] User 'Jofredsteyn' not found")

    print()
    print("=" * 80)
