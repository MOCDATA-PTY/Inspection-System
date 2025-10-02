#!/usr/bin/env python3
"""
Check inspector mapping for test user
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

def check_inspector_mapping():
    """Check inspector mapping for test user"""
    print("🔍 Checking inspector mapping for test user...")
    
    try:
        # Get test user
        user = User.objects.get(username='testuser')
        print(f"👤 User: {user.username}")
        print(f"    Full name: {user.get_full_name()}")
        print(f"    Role: {user.role}")
        
        # Check for inspector mapping
        try:
            mapping = InspectorMapping.objects.get(
                inspector_name=user.get_full_name() or user.username
            )
            print(f"✅ Found mapping:")
            print(f"    Inspector ID: {mapping.inspector_id}")
            print(f"    Inspector Name: {mapping.inspector_name}")
            print(f"    Is Active: {mapping.is_active}")
        except InspectorMapping.DoesNotExist:
            print("❌ No inspector mapping found")
            
            # Check if there are any mappings at all
            all_mappings = InspectorMapping.objects.all()
            print(f"📊 Total mappings in database: {all_mappings.count()}")
            
            if all_mappings.count() > 0:
                print("📋 Sample mappings:")
                for mapping in all_mappings[:5]:
                    print(f"    {mapping.inspector_name} -> ID {mapping.inspector_id}")
            
            # Try to find a mapping by username
            try:
                mapping_by_username = InspectorMapping.objects.get(
                    inspector_name=user.username
                )
                print(f"✅ Found mapping by username:")
                print(f"    Inspector ID: {mapping_by_username.inspector_id}")
            except InspectorMapping.DoesNotExist:
                print("❌ No mapping found by username either")
                
                # Create a mapping for the test user
                print("🔧 Creating mapping for test user...")
                
                # Find an available inspector ID
                from main.models import FoodSafetyAgencyInspection
                used_ids = set(InspectorMapping.objects.values_list('inspector_id', flat=True))
                available_inspector = FoodSafetyAgencyInspection.objects.exclude(
                    inspector_id__in=used_ids
                ).first()
                
                if available_inspector:
                    mapping = InspectorMapping.objects.create(
                        inspector_id=available_inspector.inspector_id,
                        inspector_name=user.get_full_name() or user.username,
                        is_active=True
                    )
                    print(f"✅ Created mapping: {mapping.inspector_name} -> ID {mapping.inspector_id}")
                else:
                    print("❌ No available inspector IDs found")
                    
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_inspector_mapping()
