#!/usr/bin/env python3
"""
Create a test user for debugging
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

def create_test_user():
    """Create a test user for debugging"""
    print("🔍 Creating test user...")
    
    try:
        # Create or get test user
        username = 'testuser'
        password = 'testpass123'
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': 'test@example.com',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            print(f"✅ Created test user: {username} / {password}")
        else:
            # Update password if user exists
            user.set_password(password)
            user.save()
            print(f"✅ Updated test user: {username} / {password}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_test_user()
