#!/usr/bin/env python3
"""
Fix mapping name to match user
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

def fix_mapping_name():
    """Fix mapping name to match user"""
    print("🔧 Fixing mapping name...")
    
    try:
        # Get test user
        user = User.objects.get(username='testuser')
        
        # Find the mapping with ID 204
        mapping = InspectorMapping.objects.get(inspector_id=204)
        print(f"📋 Current mapping: '{mapping.inspector_name}' -> ID {mapping.inspector_id}")
        
        # Update the mapping to use the username
        mapping.inspector_name = user.username
        mapping.save()
        
        print(f"✅ Updated mapping: '{mapping.inspector_name}' -> ID {mapping.inspector_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_mapping_name()
