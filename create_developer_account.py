#!/usr/bin/env python
"""
Script to create a developer account for the Food Safety Agency system.
Run this script with: python create_developer_account.py
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def create_developer_account():
    """Create a developer account."""
    
    # Developer credentials
    username = "developer"
    email = "developer@foodsafety.com"
    password = "Dev2025!"
    first_name = "System"
    last_name = "Developer"
    role = "developer"  # Developer role
    
    try:
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"User '{username}' already exists. Skipping user creation.")
            user = User.objects.get(username=username)
        else:
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role  # Set role to developer
            )
            print(f"✅ Created user: {username}")
        
        print("\n" + "="*50)
        print("👨‍💻 DEVELOPER ACCOUNT CREDENTIALS:")
        print("="*50)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Email: {email}")
        print(f"Full Name: {first_name} {last_name}")
        print(f"Role: Developer")
        print("="*50)
        print("\n📝 DEVELOPER PERMISSIONS:")
        print("• Access to all system features")
        print("• Database management capabilities")
        print("• System configuration access")
        print("• Development and debugging tools")
        print("• Highest level of system access")
        print("="*50)
        print("\n⚠️  SECURITY NOTE:")
        print("• This account has the highest privileges")
        print("• Use only for development and system administration")
        print("• Change the password after first login")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error creating developer account: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Creating developer account...")
    success = create_developer_account()
    
    if success:
        print("\n🎉 Developer account created successfully!")
        print("You can now login with the credentials shown above.")
    else:
        print("\n❌ Failed to create developer account.")
        print("Please check the error message above.")
