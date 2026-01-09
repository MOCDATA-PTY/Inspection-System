#!/usr/bin/env python3
"""
Fix user role to developer
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

def fix_user_role():
    """Fix user role to developer"""
    print("🔧 Fixing user role to developer...")
    
    try:
        # Get test user
        user = User.objects.get(username='testuser')
        print(f"👤 User: {user.username}")
        print(f"    Current role: {user.role}")
        
        # Update role to developer
        user.role = 'developer'
        user.save()
        
        print(f"✅ Updated role to: {user.role}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_user_role()
