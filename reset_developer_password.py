#!/usr/bin/env python
"""
Script to reset the developer account password.
Run this script with: python reset_developer_password.py
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

def reset_developer_password():
    """Reset the developer account password."""
    
    username = "developer"
    new_password = "Dev2025!"
    
    try:
        # Check if user exists
        if not User.objects.filter(username=username).exists():
            print(f"❌ User '{username}' does not exist!")
            return False
        
        # Get the user
        user = User.objects.get(username=username)
        
        # Reset the password
        user.set_password(new_password)
        user.save()
        
        print(f"✅ Password reset successfully for user: {username}")
        
        print("\n" + "="*50)
        print("👨‍💻 UPDATED DEVELOPER CREDENTIALS:")
        print("="*50)
        print(f"Username: {username}")
        print(f"Password: {new_password}")
        print(f"Email: {user.email}")
        print(f"Full Name: {user.first_name} {user.last_name}")
        print(f"Role: {getattr(user, 'role', 'N/A')}")
        print("="*50)
        print("\n🔐 LOGIN INSTRUCTIONS:")
        print("1. Go to your login page")
        print("2. Enter username: developer")
        print("3. Enter password: Dev2025!")
        print("4. Click Login")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting password: {str(e)}")
        return False

if __name__ == "__main__":
    print("Resetting developer account password...")
    success = reset_developer_password()
    
    if success:
        print("\n🎉 Password reset completed!")
        print("You should now be able to login with the new credentials.")
    else:
        print("\n❌ Failed to reset password.")
        print("Please check the error message above.")
