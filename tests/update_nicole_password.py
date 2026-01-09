#!/usr/bin/env python3
"""
Script to update Nicole's password to Nicole2025!
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

if __name__ == '__main__':
    print("=" * 100)
    print("UPDATING NICOLE'S PASSWORD")
    print("=" * 100)
    print()
    
    try:
        # Find Nicole user
        nicole_user = User.objects.filter(username__iexact='nicole').first()
        
        if nicole_user:
            # Update password
            nicole_user.set_password('Nicole2025!')
            nicole_user.save()
            
            print(f"✅ Successfully updated password for Nicole")
            print(f"   Username: {nicole_user.username}")
            print(f"   Full Name: {nicole_user.get_full_name()}")
            print(f"   Email: {nicole_user.email or 'N/A'}")
            print(f"   Role: {getattr(nicole_user, 'role', 'N/A')}")
            print(f"   New Password: Nicole2025!")
            print()
            print("=" * 100)
            print("✅ Password updated successfully!")
            print("=" * 100)
        else:
            print("❌ User 'Nicole' not found")
            
    except Exception as e:
        print(f"❌ Error updating password: {str(e)}")
        import traceback
        traceback.print_exc()

