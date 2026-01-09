#!/usr/bin/env python3
"""
Script to reset passwords for all failed inspector logins
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
    print("RESETTING FAILED INSPECTOR PASSWORDS")
    print("=" * 80)
    print()

    # List of failed accounts with their expected passwords
    failed_accounts = {
        'Ben': 'BENVISAGIE@2024',
        'Chrisdelport': 'ChrisDelport@2024',
        'Cinga': 'CINGANGONGO@2024',
        'Gladys': 'GLADYSMANGANYE@2024',
        'Jofred': 'JOFREDSTEYN@2024',
        'Kutlwano': 'KUTLWANOKUNTWANE@2024',
        'Lebogang': 'LebogangSekgobane@2024',
        'Lwandile': 'LWANDILEMAQINA@2024',
        'Mokgadiselone': 'MOKGADISELONE@2024',
        'Nelisa': 'NELISANTOYAPHI@2024',
        'Nicole': 'Nicole@2024',
        'Nthabiseng': 'NthabisengMaseko@2024',
        'Sandisiwe': 'SANDISIWEDLISANI@2024',
        'Simphiwe': 'SimphiweMathenjwa@2024',
        'Thato': 'THATOSEKHOTHO@2024',
        'Xola': 'XOLAMPELUZA@2024',
    }

    success_count = 0
    verify_count = 0

    print(f"Resetting passwords for {len(failed_accounts)} inspectors...")
    print()

    for username, password in failed_accounts.items():
        user = User.objects.filter(username=username).first()

        if user:
            # Reset password
            user.set_password(password)
            user.save()
            print(f"[RESET] {username:20s} - Password set to: {password}")
            success_count += 1

            # Verify the reset worked
            auth_user = authenticate(username=username, password=password)
            if auth_user:
                print(f"        {username:20s} - Verification: LOGIN SUCCESSFUL [OK]")
                verify_count += 1
            else:
                print(f"        {username:20s} - Verification: LOGIN FAILED [FAIL]")
        else:
            print(f"[ERROR] {username:20s} - User not found")
        print()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total accounts to reset: {len(failed_accounts)}")
    print(f"Passwords successfully reset: {success_count}")
    print(f"Login verification passed: {verify_count}")
    print()
    print("=" * 80)
