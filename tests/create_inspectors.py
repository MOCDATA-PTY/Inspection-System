#!/usr/bin/env python3
"""
Script to create inspector accounts from email list
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# List of inspector emails from the email
inspector_emails = [
    'neonoe@afsq.co.za',
    'cinga.ngongo@afsq.co.za',
    'ben.visagie@afsq.co.za',
    'percy.maleka@afsq.co.za',
    'thato.sekhotho@afsq.co.za',
    'lwandile.maqina@afsq.co.za',
    'jofred.steyn@afsq.co.za',
    'xola.mpeluza@afsq.co.za',
    'sandisiwe.dlisani@afsq.co.za',
    'gladys.manganye@afsq.co.za',
    'mokgadi.seloane@afsq.co.za',
    'kutlwano.kuntwane@afsq.co.za',
    'nelisa.ntoyaphi@afsq.co.za',
    'dimakatso.modiba@afsq.co.za',
    'cornelius.adams@afsq.co.za',
    'lebogang.sekgobane@afsq.co.za',
]

if __name__ == '__main__':
    print("=" * 80)
    print("CREATING INSPECTOR ACCOUNTS")
    print("=" * 80)
    print()

    created_count = 0
    existing_count = 0

    for email in inspector_emails:
        # Extract name from email (part before @)
        email_prefix = email.split('@')[0]

        # Extract first and last name
        if '.' in email_prefix:
            parts = email_prefix.split('.')
            first_name = parts[0].capitalize()
            last_name = parts[1].capitalize() if len(parts) > 1 else ''
        else:
            first_name = email_prefix.capitalize()
            last_name = ''

        # Create username (lowercase, no dots)
        username = email_prefix.replace('.', '').lower()

        # Check if user already exists
        existing_user = User.objects.filter(username__iexact=username).first()

        if existing_user:
            print(f"[OK] User already exists: {username} ({first_name} {last_name})")
            print(f"  Email: {existing_user.email}")
            print(f"  Role: {existing_user.role if hasattr(existing_user, 'role') else 'N/A'}")
            existing_count += 1
        else:
            # Create new user
            # Default password pattern: FirstLast@2024
            default_password = f"{first_name}{last_name}@2024"

            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=default_password
                )

                # Set role to inspector
                if hasattr(user, 'role'):
                    user.role = 'inspector'
                    user.save()

                print(f"[CREATED] New user: {username}")
                print(f"  Name: {first_name} {last_name}")
                print(f"  Email: {email}")
                print(f"  Password: {default_password}")
                print(f"  Role: inspector")
                created_count += 1
            except Exception as e:
                print(f"[ERROR] Error creating user {username}: {e}")

        print()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total emails processed: {len(inspector_emails)}")
    print(f"Existing users: {existing_count}")
    print(f"New users created: {created_count}")
    print("=" * 80)
