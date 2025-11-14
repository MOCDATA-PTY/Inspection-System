#!/usr/bin/env python3
"""
Script to update email addresses for existing users
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
    print("UPDATING USER EMAIL ADDRESSES")
    print("=" * 80)
    print()

    # Map username to email
    email_updates = {
        'cinga': 'cinga.ngongo@afsq.co.za',
        'mokgadiselone': 'mokgadi.seloane@afsq.co.za',
        'lebogang': 'lebogang.sekgobane@afsq.co.za',
        'Neo': 'neonoe@afsq.co.za',
    }

    for username, email in email_updates.items():
        user = User.objects.filter(username=username).first()
        if user:
            old_email = user.email
            user.email = email
            user.save()
            print(f"[UPDATED] {username}")
            print(f"  Old Email: {old_email}")
            print(f"  New Email: {email}")
        else:
            print(f"[NOT FOUND] User '{username}' not found")
        print()

    print("=" * 80)
    print("EMAIL UPDATE COMPLETE")
    print("=" * 80)
