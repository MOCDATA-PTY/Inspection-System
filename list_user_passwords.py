#!/usr/bin/env python3
"""
Script to list users and their password information
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

if __name__ == '__main__':
    print("=" * 100)
    print("USER PASSWORDS SUMMARY")
    print("=" * 100)
    print()
    
    # Users we just created/updated
    users_to_check = ['mpho', 'admin', 'Nicole']
    
    print("RECENTLY CREATED/UPDATED USERS:")
    print("-" * 100)
    print()
    
    for username in users_to_check:
        try:
            user = User.objects.get(username__iexact=username)
            print(f"Username: {user.username}")
            print(f"  Full Name: {user.get_full_name()}")
            print(f"  Email: {user.email or 'N/A'}")
            print(f"  Role: {getattr(user, 'role', 'N/A')}")
            print(f"  Active: {user.is_active}")
            print(f"  Staff: {user.is_staff}")
            print(f"  Superuser: {user.is_superuser}")
            print()
        except User.DoesNotExist:
            print(f"❌ User '{username}' not found")
            print()
    
    print("=" * 100)
    print("PASSWORDS (as set/updated):")
    print("=" * 100)
    print()
    print("1. Mpho")
    print("   Username: mpho")
    print("   Password: Mojalefa@1")
    print("   Role: admin")
    print()
    print("2. admin")
    print("   Username: admin")
    print("   Password: Admin@123")
    print("   Email: admin@afsq.co.za")
    print("   Role: admin")
    print("   Note: This is a default password - should be changed after first login")
    print()
    print("3. Nicole")
    print("   Username: Nicole")
    print("   Password: NOT SET (password was not changed in the update)")
    print("   Full Name: Nicole Bergh")
    print("   Role: financial")
    print("   Note: If you need to set a password for Nicole, please specify what it should be")
    print()
    print("=" * 100)

