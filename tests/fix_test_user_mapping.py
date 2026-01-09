#!/usr/bin/env python3
"""
Fix test user mapping to use an inspector with actual inspections
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import InspectorMapping, FoodSafetyAgencyInspection
from django.contrib.auth.models import User
from datetime import datetime, timedelta

def fix_test_user_mapping():
    """Fix test user mapping to use an inspector with actual inspections"""
    print("🔧 Fixing test user mapping...")
    
    try:
        # Get test user
        user = User.objects.get(username='testuser')
        
        # Find an inspector ID that has recent inspections
        six_months_ago = datetime.now() - timedelta(days=180)
        
        # Get inspector IDs with recent inspections
        recent_inspector_ids = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection__gte=six_months_ago
        ).values_list('inspector_id', flat=True).distinct()
        
        print(f"📊 Found {len(recent_inspector_ids)} inspector IDs with recent inspections")
        
        # Find one that doesn't have a mapping yet
        used_ids = set(InspectorMapping.objects.values_list('inspector_id', flat=True))
        available_ids = [id for id in recent_inspector_ids if id not in used_ids]
        
        if available_ids:
            inspector_id = available_ids[0]
            print(f"✅ Using inspector ID: {inspector_id}")
            
            # Get inspector name
            inspector_name = FoodSafetyAgencyInspection.objects.filter(
                inspector_id=inspector_id
            ).values_list('inspector_name', flat=True).first()
            
            print(f"📋 Inspector name: {inspector_name}")
            
            # Count inspections for this inspector
            inspection_count = FoodSafetyAgencyInspection.objects.filter(
                inspector_id=inspector_id,
                date_of_inspection__gte=six_months_ago
            ).count()
            print(f"📊 Recent inspections: {inspection_count}")
            
            # Update the test user's mapping
            mapping = InspectorMapping.objects.get(
                inspector_name=user.get_full_name() or user.username
            )
            mapping.inspector_id = inspector_id
            mapping.inspector_name = inspector_name
            mapping.save()
            
            print(f"✅ Updated mapping: {mapping.inspector_name} -> ID {mapping.inspector_id}")
            
            return True
        else:
            print("❌ No available inspector IDs found")
            
            # Just use the first available inspector ID
            first_id = recent_inspector_ids[0]
            print(f"🔧 Using first available ID: {first_id}")
            
            # Get inspector name
            inspector_name = FoodSafetyAgencyInspection.objects.filter(
                inspector_id=first_id
            ).values_list('inspector_name', flat=True).first()
            
            # Update the test user's mapping
            mapping = InspectorMapping.objects.get(
                inspector_name=user.get_full_name() or user.username
            )
            mapping.inspector_id = first_id
            mapping.inspector_name = inspector_name
            mapping.save()
            
            print(f"✅ Updated mapping: {mapping.inspector_name} -> ID {mapping.inspector_id}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_test_user_mapping()
