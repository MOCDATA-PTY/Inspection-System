#!/usr/bin/env python3
"""
Script to find user with nthabiseng.maseki email
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
    print("SEARCHING FOR NTHABISENG.MASEKI@FSA-PTY.CO.ZA")
    print("=" * 80)
    print()

    # Search for exact email
    user = User.objects.filter(email='nthabiseng.maseki@fsa-pty.co.za').first()

    if user:
        print(f"[FOUND] User with email nthabiseng.maseki@fsa-pty.co.za")
        print(f"  Username: {user.username}")
        print(f"  Name: {user.first_name} {user.last_name}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role if hasattr(user, 'role') else 'N/A'}")
        print(f"  Is Active: {user.is_active}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")
    else:
        print("[NOT FOUND] No user with email nthabiseng.maseki@fsa-pty.co.za")
        print()
        print("Searching for similar emails with 'masek'...")
        similar = User.objects.filter(email__icontains='masek')
        if similar.exists():
            for u in similar:
                print(f"  Found: {u.username} - {u.email} - Role: {u.role if hasattr(u, 'role') else 'N/A'}")
        else:
            print("  No similar emails found")

    print()
    print("=" * 80)
