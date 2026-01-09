#!/usr/bin/env python3
"""
Script to update passwords for Xola, Thato, and Lwandile
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction

def update_passwords():
    """Update passwords for Xola, Thato, and Lwandile"""
    print("=" * 80)
    print("UPDATING USER PASSWORDS")
    print("=" * 80)
    print()
    
    # Password updates to make
    password_updates = [
        {'username': 'Xola', 'password': 'Mpeluza@1993', 'full_name': 'XOLA MPELUZA'},
        {'username': 'Thato', 'password': '123Abc123@', 'full_name': 'THATO SEKHOTHO'},
        {'username': 'Lwandile', 'password': 'Lw@ndile1', 'full_name': 'LWANDILE MAQINA'},
    ]
    
    try:
        with transaction.atomic():
            for update in password_updates:
                username = update['username']
                new_password = update['password']
                full_name = update['full_name']
                
                print(f"🔐 Updating password for: {username}")
                print("-" * 80)
                
                # Try to find user by username (case-insensitive)
                try:
                    user = User.objects.get(username__iexact=username)
                except User.DoesNotExist:
                    # Try searching by first name or last name
                    from django.db import models
                    user = User.objects.filter(
                        models.Q(first_name__iexact=username) | 
                        models.Q(last_name__iexact=username) |
                        models.Q(username__icontains=username.lower())
                    ).first()
                    
                    if not user:
                        # Try by full name match
                        users = User.objects.all()
                        for u in users:
                            if u.get_full_name().upper() == full_name.upper():
                                user = u
                                break
                
                if user:
                    # Change the password
                    user.set_password(new_password)
                    user.save()
                    
                    print(f"✅ Successfully updated password for:")
                    print(f"   Username: {user.username}")
                    print(f"   Full Name: {user.get_full_name()}")
                    print(f"   Email: {user.email or 'N/A'}")
                    print(f"   Role: {getattr(user, 'role', 'N/A')}")
                    print(f"   Active: {user.is_active}")
                    print(f"   New Password: {new_password}")
                    print()
                else:
                    print(f"❌ User '{username}' not found in the system")
                    print()
            
            print("=" * 80)
            print("✅ Password updates completed!")
            print("=" * 80)
            return True
                    
    except Exception as e:
        print(f"❌ Error updating passwords: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = update_passwords()
        if success:
            print("\n✅ All password updates completed successfully!")
        else:
            print("\n❌ Some password updates failed. Check the output above.")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

