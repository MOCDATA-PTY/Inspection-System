#!/usr/bin/env python3
"""
Script to find duplicate users
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
    print("FINDING DUPLICATE USERS")
    print("=" * 80)
    print()

    # Check for users with similar names
    all_users = User.objects.all().order_by('first_name', 'last_name')

    duplicates = []

    # Group by similar first/last names
    for user in all_users:
        first_name_lower = user.first_name.lower() if user.first_name else ''
        last_name_lower = user.last_name.lower() if user.last_name else ''

        # Find potential duplicates
        similar_users = User.objects.filter(
            first_name__iexact=user.first_name
        ).exclude(id=user.id)

        if similar_users.exists():
            print(f"Potential duplicates for {user.first_name} {user.last_name}:")
            print(f"  Original: ID={user.id}, Username={user.username}, Email={user.email}")
            for sim in similar_users:
                print(f"  Duplicate: ID={sim.id}, Username={sim.username}, Email={sim.email}")
            print()

    print("=" * 80)
    print("SPECIFIC DUPLICATES TO DELETE")
    print("=" * 80)
    print()

    # List specific duplicates to delete
    users_to_check = [
        ('cinga', 'cingangongo'),  # Keep cinga, delete cingangongo
        ('mokgadiselone', 'mokgadiseloane'),  # Keep mokgadiselone, delete mokgadiseloane
        ('lebogang', 'lebogangsekgobane'),  # Keep lebogang, delete lebogangsekgobane
    ]

    for keep_username, delete_username in users_to_check:
        keep_user = User.objects.filter(username=keep_username).first()
        delete_user = User.objects.filter(username=delete_username).first()

        if keep_user and delete_user:
            print(f"DUPLICATE FOUND:")
            print(f"  KEEP: {keep_user.username} (ID: {keep_user.id}) - {keep_user.first_name} {keep_user.last_name}")
            print(f"  DELETE: {delete_user.username} (ID: {delete_user.id}) - {delete_user.first_name} {delete_user.last_name}")
            print()
