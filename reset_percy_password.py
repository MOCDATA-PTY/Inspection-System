#!/usr/bin/env python3
"""
Script to reset Percy's password and verify login
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

if __name__ == '__main__':
    print("=" * 80)
    print("RESETTING PERCY'S PASSWORD")
    print("=" * 80)
    print()

    user = User.objects.filter(username='Percy').first()

    if user:
        # Set new password
        new_password = 'Percy@2024'
        user.set_password(new_password)
        user.save()

        print(f"[SUCCESS] Password reset for Percy")
        print(f"  Username: Percy")
        print(f"  New Password: {new_password}")
        print()

        # Try to authenticate with new password
        print("Testing login with new password...")
        auth_user = authenticate(username='Percy', password=new_password)

        if auth_user:
            print("[SUCCESS] Login test passed!")
            print(f"  Authenticated as: {auth_user.username}")
            print(f"  Name: {auth_user.first_name} {auth_user.last_name}")
            print(f"  Role: {auth_user.role if hasattr(auth_user, 'role') else 'N/A'}")
        else:
            print("[FAILED] Login test failed - authentication did not work")
    else:
        print(f"[NOT FOUND] User 'Percy' not found")

    print()
    print("=" * 80)
