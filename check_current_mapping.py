#!/usr/bin/env python3
"""
Check current mapping for test user
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import InspectorMapping
from django.contrib.auth.models import User

def check_current_mapping():
    """Check current mapping for test user"""
    print("🔍 Checking current mapping for test user...")
    
    try:
        # Get test user
        user = User.objects.get(username='testuser')
        print(f"👤 User: {user.username}")
        print(f"    Full name: '{user.get_full_name()}'")
        print(f"    Username: '{user.username}'")
        
        # Check all mappings
        all_mappings = InspectorMapping.objects.all()
        print(f"📊 Total mappings: {all_mappings.count()}")
        
        print("📋 All mappings:")
        for mapping in all_mappings:
            print(f"    '{mapping.inspector_name}' -> ID {mapping.inspector_id}")
            
        # Try to find mapping by username
        try:
            mapping_by_username = InspectorMapping.objects.get(inspector_name=user.username)
            print(f"✅ Found mapping by username: {mapping_by_username.inspector_name} -> ID {mapping_by_username.inspector_id}")
        except InspectorMapping.DoesNotExist:
            print("❌ No mapping found by username")
            
        # Try to find mapping by full name
        try:
            mapping_by_full_name = InspectorMapping.objects.get(inspector_name=user.get_full_name() or user.username)
            print(f"✅ Found mapping by full name: {mapping_by_full_name.inspector_name} -> ID {mapping_by_full_name.inspector_id}")
        except InspectorMapping.DoesNotExist:
            print("❌ No mapping found by full name")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_current_mapping()
