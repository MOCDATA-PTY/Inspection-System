#!/usr/bin/env python3
"""
Script to test login for all inspector accounts
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
    print("TESTING ALL INSPECTOR LOGINS")
    print("=" * 80)
    print()

    inspectors = User.objects.filter(role='inspector').order_by('username')

    # List of known passwords based on the pattern
    test_passwords = {
        'Ben': 'BENVISAGIE@2024',
        'Chrisdelport': 'ChrisDelport@2024',
        'Cinga': 'CINGANGONGO@2024',
        'Cornelius': 'CorneliusAdams@2024',
        'Dimakatso': 'DimakatsoModiba@2024',
        'Gladys': 'GLADYSMANGANYE@2024',
        'Jofred': 'JOFREDSTEYN@2024',
        'Kutlwano': 'KUTLWANOKUNTWANE@2024',
        'Lebogang': 'LebogangSekgobane@2024',
        'Lwandile': 'LWANDILEMAQINA@2024',
        'Mokgadiselone': 'MOKGADISELONE@2024',
        'Nelisa': 'NELISANTOYAPHI@2024',
        'Neo': 'Neon@0127',  # Custom password
        'Nicole': 'Nicole@2024',
        'Nthabiseng': 'NthabisengMaseko@2024',
        'Percy': 'Percy@2024',  # Recently reset
        'Sandisiwe': 'SANDISIWEDLISANI@2024',
        'Simphiwe': 'SimphiweMathenjwa@2024',
        'Thato': 'THATOSEKHOTHO@2024',
        'Xola': 'XOLAMPELUZA@2024',
    }

    success_count = 0
    failed_count = 0
    failed_logins = []

    print(f"Testing {inspectors.count()} inspector accounts...")
    print()

    for inspector in inspectors:
        username = inspector.username
        password = test_passwords.get(username, 'Unknown')

        # Try to authenticate
        auth_user = authenticate(username=username, password=password)

        if auth_user:
            print(f"[OK] {username:20s} - Login successful")
            success_count += 1
        else:
            print(f"[FAIL] {username:20s} - Login failed (Password: {password})")
            failed_count += 1
            failed_logins.append({
                'username': username,
                'name': f"{inspector.first_name} {inspector.last_name}",
                'email': inspector.email if inspector.email else 'Not set',
                'password': password
            })

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total inspectors tested: {inspectors.count()}")
    print(f"Successful logins: {success_count}")
    print(f"Failed logins: {failed_count}")
    print()

    if failed_logins:
        print("=" * 80)
        print("FAILED LOGINS - NEED PASSWORD RESET")
        print("=" * 80)
        print()
        for failed in failed_logins:
            print(f"Username: {failed['username']}")
            print(f"  Name: {failed['name']}")
            print(f"  Email: {failed['email']}")
            print(f"  Tested Password: {failed['password']}")
            print()

    print("=" * 80)
