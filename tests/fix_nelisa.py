#!/usr/bin/env python3
"""
Script to fix Nelisantoyaphi to Nelisa
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
    print("FIXING NELISA USERNAME")
    print("=" * 80)
    print()

    user = User.objects.filter(username='Nelisantoyaphi').first()

    if user:
        # Check if new username already exists
        existing = User.objects.filter(username='Nelisa').exclude(id=user.id).first()
        if existing:
            print(f"[ERROR] Cannot change - username 'Nelisa' already exists")
        else:
            user.username = 'Nelisa'
            user.save()
            print(f"[FIXED] Nelisantoyaphi -> Nelisa")
    else:
        print(f"[NOT FOUND] User 'Nelisantoyaphi' not found")

    print()
    print("=" * 80)
