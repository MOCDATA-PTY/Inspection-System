#!/usr/bin/env python3
"""
Clean up test user and use existing developer account
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
from main.models import InspectorMapping

def cleanup_test_user():
    """Clean up test user and use existing developer account"""
    print("🧹 Cleaning up test user...")
    
    try:
        # Remove test user
        try:
            test_user = User.objects.get(username='testuser')
            print(f"🗑️ Removing test user: {test_user.username}")
            test_user.delete()
            print("✅ Test user removed")
        except User.DoesNotExist:
            print("ℹ️ Test user not found")
        
        # Remove test user mapping
        try:
            test_mapping = InspectorMapping.objects.get(inspector_name='testuser')
            print(f"🗑️ Removing test user mapping: {test_mapping.inspector_name}")
            test_mapping.delete()
            print("✅ Test user mapping removed")
        except InspectorMapping.DoesNotExist:
            print("ℹ️ Test user mapping not found")
        
        # Check developer account
        try:
            developer = User.objects.get(username='developer')
            print(f"👤 Developer account found:")
            print(f"    Username: {developer.username}")
            print(f"    Email: {developer.email}")
            print(f"    Role: {developer.role}")
            print(f"    Is active: {developer.is_active}")
            print(f"    Is staff: {developer.is_staff}")
            print(f"    Is superuser: {developer.is_superuser}")
            
            # Ensure developer has correct role
            if developer.role != 'developer':
                developer.role = 'developer'
                developer.save()
                print("✅ Updated developer role")
            
            print("\n🎉 Ready to use developer account!")
            print("   Username: developer")
            print("   Password: Dev2025!")
            
        except User.DoesNotExist:
            print("❌ Developer account not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    cleanup_test_user()
