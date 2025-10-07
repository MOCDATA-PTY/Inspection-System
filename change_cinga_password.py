#!/usr/bin/env python3
"""
Script to change password for user 'cinga' to 'Banoyolo@08'
This script can be run directly from the project root directory.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def change_cinga_password():
    """Change password for user cinga to Banoyolo@08"""
    print("🔐 Changing password for user 'cinga'")
    print("=" * 50)
    
    from django.contrib.auth.models import User
    from django.db import transaction
    
    username = 'cinga'
    new_password = 'Banoyolo@08'
    
    try:
        with transaction.atomic():
            # Try to find user by exact username first
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Try case-insensitive search
                user = User.objects.filter(username__iexact=username).first()
                if not user:
                    # Try searching by first name or last name containing 'cinga'
                    from django.db import models
                    user = User.objects.filter(
                        models.Q(first_name__icontains='cinga') | 
                        models.Q(last_name__icontains='cinga')
                    ).first()
            
            if user:
                # Change the password
                user.set_password(new_password)
                user.save()
                
                print(f"✅ Successfully changed password for user: {user.username}")
                print(f"   Full name: {user.get_full_name()}")
                print(f"   Email: {user.email}")
                print(f"   Role: {getattr(user, 'role', 'N/A')}")
                print(f"   Active: {user.is_active}")
                print(f"   New password: {new_password}")
                
            else:
                print(f"❌ User '{username}' not found in the system")
                
                # Show available users for reference
                print("\n📋 Available users in the system:")
                print("-" * 40)
                users = User.objects.all().order_by('username')
                for u in users:
                    print(f"  • {u.username} ({u.get_full_name()}) - {u.email}")
                    
    except Exception as e:
        print(f"❌ Error changing password: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = change_cinga_password()
        if success:
            print("\n🎉 Password change completed successfully!")
        else:
            print("\n💥 Password change failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Script failed with error: {str(e)}")
        sys.exit(1)
