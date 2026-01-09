#!/usr/bin/env python3
"""
Script to update admin user's password to admin123
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

if __name__ == '__main__':
    print("=" * 100)
    print("UPDATING ADMIN USER'S PASSWORD")
    print("=" * 100)
    print()
    
    try:
        # Find admin user
        admin_user = User.objects.filter(username__iexact='admin').first()
        
        if admin_user:
            # Update password
            admin_user.set_password('admin2025!')
            admin_user.save()
            
            print(f"✅ Successfully updated password for admin")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email or 'N/A'}")
            print(f"   Role: {getattr(admin_user, 'role', 'N/A')}")
            print(f"   New Password: admin2025!")
            print()
            print("=" * 100)
            print("✅ Password updated successfully!")
            print("=" * 100)
        else:
            print("❌ User 'admin' not found")
            
    except Exception as e:
        print(f"❌ Error updating password: {str(e)}")
        import traceback
        traceback.print_exc()

