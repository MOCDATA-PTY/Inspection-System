#!/usr/bin/env python3
"""
Check what users exist in the system
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def check_users():
    """Check what users exist"""
    print("🔍 Checking users in the system...")
    
    try:
        users = User.objects.all()
        print(f"📊 Found {users.count()} users:")
        
        for user in users:
            print(f"    Username: {user.username}")
            print(f"    Email: {user.email}")
            print(f"    Is active: {user.is_active}")
            print(f"    Is staff: {user.is_staff}")
            print(f"    Is superuser: {user.is_superuser}")
            print(f"    Last login: {user.last_login}")
            print("    ---")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_users()
