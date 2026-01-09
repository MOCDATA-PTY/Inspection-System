#!/usr/bin/env python3
"""
Script to create/update users: Mpho, admin, and Nicole
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction

def create_update_users():
    """Create or update users as requested"""
    print("=" * 100)
    print("CREATING/UPDATING USERS")
    print("=" * 100)
    print()
    
    try:
        with transaction.atomic():
            # 1. Mpho - Update password to Mojalefa@1 (role should be admin, not super_admin)
            print("1. Handling Mpho...")
            print("-" * 100)
            
            mpho_user = User.objects.filter(username__iexact='mpho').first()
            
            if mpho_user:
                print(f"✅ Found existing user: {mpho_user.username}")
                print(f"   Current role: {getattr(mpho_user, 'role', 'N/A')}")
                
                # Update password
                mpho_user.set_password('Mojalefa@1')
                
                # Ensure role is admin (not super_admin)
                mpho_user.role = 'admin'
                mpho_user.is_staff = True  # Admin should have staff access
                mpho_user.is_superuser = False  # Not super_admin
                mpho_user.save()
                
                print(f"✅ Updated Mpho:")
                print(f"   Username: {mpho_user.username}")
                print(f"   Full Name: {mpho_user.get_full_name()}")
                print(f"   Email: {mpho_user.email or 'N/A'}")
                print(f"   Role: {mpho_user.role}")
                print(f"   Password: Mojalefa@1")
                print(f"   Is Staff: {mpho_user.is_staff}")
                print(f"   Is Superuser: {mpho_user.is_superuser}")
            else:
                # Create new Mpho user
                mpho_user = User.objects.create_user(
                    username='mpho',
                    password='Mojalefa@1',
                    first_name='Mpho',
                    email='mpho@afsq.co.za',
                    is_staff=True,
                    is_superuser=False
                )
                mpho_user.role = 'admin'
                mpho_user.save()
                
                print(f"✅ Created new user: Mpho")
                print(f"   Username: {mpho_user.username}")
                print(f"   Role: {mpho_user.role}")
                print(f"   Password: Mojalefa@1")
            
            print()
            
            # 2. Create user "admin" with email admin@afsq.co.za
            print("2. Handling admin user...")
            print("-" * 100)
            
            admin_user = User.objects.filter(username__iexact='admin').first()
            
            if admin_user:
                print(f"⚠️  User 'admin' already exists:")
                print(f"   Username: {admin_user.username}")
                print(f"   Email: {admin_user.email or 'N/A'}")
                print(f"   Role: {getattr(admin_user, 'role', 'N/A')}")
                print()
                print("   Updating email to admin@afsq.co.za...")
                admin_user.email = 'admin@afsq.co.za'
                admin_user.save()
                print(f"   ✅ Email updated to: {admin_user.email}")
            else:
                # Create new admin user
                admin_user = User.objects.create_user(
                    username='admin',
                    email='admin@afsq.co.za',
                    first_name='Admin',
                    is_staff=True,
                    is_superuser=False
                )
                admin_user.role = 'admin'  # Default to admin role
                admin_user.set_password('Admin@123')  # Set a default password
                admin_user.save()
                
                print(f"✅ Created new user: admin")
                print(f"   Username: {admin_user.username}")
                print(f"   Email: {admin_user.email}")
                print(f"   Role: {admin_user.role}")
                print(f"   Password: Admin@123 (default - should be changed)")
            
            print()
            
            # 3. Update Nicole - add surname Bergh and make her financial admin
            print("3. Handling Nicole...")
            print("-" * 100)
            
            nicole_user = User.objects.filter(username__iexact='nicole').first()
            
            if nicole_user:
                print(f"✅ Found existing user: {nicole_user.username}")
                print(f"   Current Full Name: {nicole_user.get_full_name()}")
                print(f"   Current First Name: {nicole_user.first_name}")
                print(f"   Current Last Name: {nicole_user.last_name}")
                print(f"   Current Role: {getattr(nicole_user, 'role', 'N/A')}")
                print()
                
                # Update surname to Bergh
                nicole_user.last_name = 'Bergh'
                if not nicole_user.first_name:
                    nicole_user.first_name = 'Nicole'
                
                # Update role to financial
                nicole_user.role = 'financial'
                nicole_user.is_staff = True  # Financial admin should have staff access
                nicole_user.is_superuser = False  # Not superuser
                nicole_user.save()
                
                print(f"✅ Updated Nicole:")
                print(f"   Username: {nicole_user.username}")
                print(f"   Full Name: {nicole_user.get_full_name()}")
                print(f"   Email: {nicole_user.email or 'N/A'}")
                print(f"   Role: {nicole_user.role}")
                print(f"   Is Staff: {nicole_user.is_staff}")
                print(f"   Is Superuser: {nicole_user.is_superuser}")
            else:
                # Create new Nicole user
                nicole_user = User.objects.create_user(
                    username='nicole',
                    email='nicole.bergh@afsq.co.za',
                    first_name='Nicole',
                    last_name='Bergh',
                    is_staff=True,
                    is_superuser=False
                )
                nicole_user.role = 'financial'
                nicole_user.set_password('Nicole@123')  # Set a default password
                nicole_user.save()
                
                print(f"✅ Created new user: Nicole")
                print(f"   Username: {nicole_user.username}")
                print(f"   Full Name: {nicole_user.get_full_name()}")
                print(f"   Role: {nicole_user.role}")
                print(f"   Password: Nicole@123 (default - should be changed)")
            
            print()
            print("=" * 100)
            print("✅ ALL USERS CREATED/UPDATED SUCCESSFULLY!")
            print("=" * 100)
            print()
            print("Summary:")
            print("  1. Mpho - Password: Mojalefa@1, Role: admin")
            print("  2. admin - Email: admin@afsq.co.za")
            print("  3. Nicole - Surname: Bergh, Role: financial")
            print()
            
            return True
                    
    except Exception as e:
        print(f"❌ Error creating/updating users: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = create_update_users()
        if not success:
            print("\n❌ Some operations failed. Check the output above.")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

