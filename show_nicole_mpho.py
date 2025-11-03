#!/usr/bin/env python3
"""
Script to show Nicole and Mpho's account details
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
    print("NICOLE AND MPHO ACCOUNT DETAILS")
    print("=" * 80)
    print()

    # Find Nicole
    nicole = User.objects.filter(username__iexact='Nicole').first()
    if nicole:
        print("NICOLE:")
        print(f"  Username: {nicole.username}")
        print(f"  Email: {nicole.email if nicole.email else 'Not set'}")
        print(f"  Name: {nicole.first_name} {nicole.last_name}")
        print(f"  Role: {nicole.role if hasattr(nicole, 'role') else 'N/A'}")
        print(f"  Password: (Cannot retrieve - encrypted)")
        print(f"  Note: Password likely follows FirstLast@2024 format")
    else:
        print("Nicole: Not found")

    print()

    # Find Mpho
    mpho = User.objects.filter(username__iexact='mpho').first()
    if mpho:
        print("MPHO:")
        print(f"  Username: {mpho.username}")
        print(f"  Email: {mpho.email if mpho.email else 'Not set'}")
        print(f"  Name: {mpho.first_name} {mpho.last_name}")
        print(f"  Role: {mpho.role if hasattr(mpho, 'role') else 'N/A'}")
        print(f"  Password: (Cannot retrieve - encrypted)")
        print(f"  Note: Password was mentioned in emails as 'Mojalefa@1'")
    else:
        print("Mpho: Not found")

    print()
    print("=" * 80)
    print("Note: Passwords are encrypted and cannot be retrieved.")
    print("Based on email context from earlier:")
    print("  - Mpho's password: Mojalefa@1")
    print("  - Nicole's password: Likely follows FirstLast@2024 pattern")
    print("=" * 80)
