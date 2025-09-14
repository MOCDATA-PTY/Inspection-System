#!/usr/bin/env python
"""
Script to create initial users for the Food Safety Agency system
Run this after setting up the new PostgreSQL database and running migrations
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def create_initial_users():
    """Create the initial users for the system"""
    
    # Define the users to create
    users_to_create = [
        {
            'username': 'admin',
            'email': 'admin@foodsafety.com',
            'password': 'admin123',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'super_admin',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'Ethan',
            'email': 'ethan@foodsafety.com',
            'password': 'Ethan4269875321',
            'first_name': 'Ethan',
            'last_name': '',
            'role': 'super_admin',
            'is_staff': True,
            'is_superuser': True
        }
    ]
    
    print("Creating initial users for Food Safety Agency system...")
    print("=" * 60)
    
    created_count = 0
    skipped_count = 0
    
    for user_data in users_to_create:
        username = user_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"⚠️  User '{username}' already exists - skipping")
            skipped_count += 1
            continue
        
        try:
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_staff=user_data['is_staff'],
                is_superuser=user_data['is_superuser']
            )
            
            # Set the role
            user.role = user_data['role']
            user.save()
            
            print(f"✅ Created user: {username}")
            print(f"   - Email: {user_data['email']}")
            print(f"   - Role: {user_data['role']}")
            print(f"   - Staff: {'Yes' if user_data['is_staff'] else 'No'}")
            print(f"   - Superuser: {'Yes' if user_data['is_superuser'] else 'No'}")
            print()
            
            created_count += 1
            
        except Exception as e:
            print(f"❌ Error creating user '{username}': {str(e)}")
            print()
    
    print("=" * 60)
    print(f"Summary:")
    print(f"- Users created: {created_count}")
    print(f"- Users skipped (already exist): {skipped_count}")
    print(f"- Total users in database: {User.objects.count()}")
    
    if created_count > 0:
        print("\n🎉 Initial users created successfully!")
        print("\nLogin credentials:")
        print("1. Username: admin, Password: admin123")
        print("2. Username: Ethan, Password: Ethan4269875321")
        print("\nBoth users have Super Admin privileges.")
    else:
        print("\nℹ️  No new users were created (they may already exist).")

def verify_users():
    """Verify that the users exist and have correct roles"""
    print("\n" + "=" * 60)
    print("VERIFYING USERS")
    print("=" * 60)
    
    users = User.objects.all()
    
    if not users.exists():
        print("❌ No users found in database!")
        return
    
    print(f"Found {users.count()} user(s) in database:")
    print()
    
    for user in users:
        role = getattr(user, 'role', 'No role')
        print(f"👤 {user.username}")
        print(f"   - Email: {user.email}")
        print(f"   - Full Name: {user.first_name} {user.last_name}".strip())
        print(f"   - Role: {role}")
        print(f"   - Active: {'Yes' if user.is_active else 'No'}")
        print(f"   - Staff: {'Yes' if user.is_staff else 'No'}")
        print(f"   - Superuser: {'Yes' if user.is_superuser else 'No'}")
        print()

if __name__ == "__main__":
    print("Food Safety Agency - Initial User Setup")
    print("=" * 60)
    
    # Create the users
    create_initial_users()
    
    # Verify the users
    verify_users()
    
    print("Setup complete! You can now log in to the system.")
