#!/usr/bin/env python3
"""
Script to delete duplicate users that were created incorrectly
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
    print("DELETING DUPLICATE USERS")
    print("=" * 80)
    print()

    # Users to delete (the ones with combined first+last names)
    users_to_delete = [
        'cingangongo',      # Keep 'cinga' instead
        'mokgadiseloane',   # Keep 'mokgadiselone' instead
        'lebogangsekgobane', # Keep 'lebogang' instead
        'neonoe',           # Keep 'Neo' instead
    ]

    for username in users_to_delete:
        user = User.objects.filter(username=username).first()
        if user:
            print(f"[DELETING] {username} (ID: {user.id}) - {user.first_name} {user.last_name}")
            print(f"  Email: {user.email}")
            user.delete()
            print(f"  >> Deleted successfully")
        else:
            print(f"[NOT FOUND] User '{username}' not found")
        print()

    print("=" * 80)
    print("DELETION COMPLETE")
    print("=" * 80)
