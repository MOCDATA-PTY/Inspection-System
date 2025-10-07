#!/usr/bin/env python3
"""
Script to rename user 'cingangongo' to 'cinga'
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

def rename_cinga_username():
    """Rename user 'cingangongo' to 'cinga'"""
    print("🔄 Renaming user 'cingangongo' to 'cinga'")
    print("=" * 50)
    
    from django.contrib.auth.models import User
    from django.db import transaction
    
    old_username = 'cingangongo'
    new_username = 'cinga'
    
    try:
        with transaction.atomic():
            # Check if old user exists
            try:
                user = User.objects.get(username=old_username)
                print(f"✅ Found user: {user.username}")
                print(f"   Full name: {user.get_full_name()}")
                print(f"   Email: {user.email}")
                print(f"   Role: {getattr(user, 'role', 'N/A')}")
                print(f"   Active: {user.is_active}")
                
                # Check if new username already exists
                if User.objects.filter(username=new_username).exists():
                    print(f"❌ Username '{new_username}' already exists!")
                    return False
                
                # Rename the user
                old_username_actual = user.username
                user.username = new_username
                user.save()
                
                print(f"✅ Successfully renamed user from '{old_username_actual}' to '{user.username}'")
                print(f"   Password remains: Banoyolo@08")
                
            except User.DoesNotExist:
                print(f"❌ User '{old_username}' not found!")
                return False
            
            # Show updated user list
            print(f"\n📋 Updated user list:")
            print("-" * 40)
            users = User.objects.all().order_by('username')
            for u in users:
                print(f"  • {u.username} ({u.get_full_name()}) - {u.email}")
                    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = rename_cinga_username()
        if success:
            print("\n🎉 Username change completed successfully!")
        else:
            print("\n💥 Username change failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Script failed with error: {str(e)}")
        sys.exit(1)
