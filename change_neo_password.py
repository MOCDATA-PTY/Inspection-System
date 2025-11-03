#!/usr/bin/env python3
"""
Script to change Neo's password
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
    print("CHANGING NEO'S PASSWORD")
    print("=" * 80)
    print()

    user = User.objects.filter(username='Neo').first()

    if user:
        new_password = 'Neon@0127'
        user.set_password(new_password)
        user.save()
        print(f"[SUCCESS] Password changed for Neo")
        print(f"  Username: Neo")
        print(f"  New Password: {new_password}")
        print(f"  Email: {user.email}")
    else:
        print(f"[NOT FOUND] User 'Neo' not found")

    print()
    print("=" * 80)
