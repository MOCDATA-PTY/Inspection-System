#!/usr/bin/env python3
"""
Debug Percy's access issue - check what's happening with the filtering
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def debug_percy_access():
    """Debug why Percy can't see his inspections"""
    print("🔍 Debugging Percy's Access Issue")
    print("=" * 60)
    
    from django.contrib.auth import get_user_model
    from main.models import InspectorMapping, FoodSafetyAgencyInspection
    from datetime import datetime, timedelta
    
    User = get_user_model()
    
    # Get Percy's user account
    try:
        percy_user = User.objects.get(username='percymaleka')
        print(f"👤 Percy's User Account:")
        print(f"   Username: {percy_user.username}")
        print(f"   First Name: '{percy_user.first_name}'")
        print(f"   Last Name: '{percy_user.last_name}'")
        print(f"   Full Name: '{percy_user.get_full_name()}'")
        print(f"   Role: {percy_user.role}")
        print()
        
        # Check what the system is looking for
        lookup_name = percy_user.get_full_name() or percy_user.username
        print(f"🔍 System will look for mapping with: '{lookup_name}'")
        
        # Check InspectorMapping
        try:
            mapping = InspectorMapping.objects.get(inspector_name=lookup_name)
            print(f"✅ Found mapping for '{lookup_name}'")
            print(f"   Inspector ID: {mapping.inspector_id}")
            print(f"   Active: {mapping.is_active}")
        except InspectorMapping.DoesNotExist:
            print(f"❌ No mapping found for '{lookup_name}'")
            
            # Try finding by username
            try:
                mapping = InspectorMapping.objects.get(inspector_name=percy_user.username)
                print(f"✅ Found mapping by username '{percy_user.username}'")
                print(f"   Inspector ID: {mapping.inspector_id}")
            except InspectorMapping.DoesNotExist:
                print(f"❌ No mapping found by username either")
                
                # Show all available mappings
                print(f"\n📋 Available InspectorMappings:")
                mappings = InspectorMapping.objects.all()
                for m in mappings:
                    print(f"   '{m.inspector_name}' → ID {m.inspector_id}")
                
                # Check if Percy exists in inspection data
                percy_inspections = FoodSafetyAgencyInspection.objects.filter(
                    inspector_name__icontains='PERCY'
                )
                if percy_inspections.exists():
                    percy_data = percy_inspections.values('inspector_name', 'inspector_id').distinct()
                    print(f"\n📊 Found Percy in inspection data:")
                    for data in percy_data:
                        print(f"   Name: '{data['inspector_name']}' → ID {data['inspector_id']}")
                        
                        # Create the missing mapping
                        try:
                            InspectorMapping.objects.create(
                                inspector_name=data['inspector_name'],
                                inspector_id=data['inspector_id'],
                                is_active=True
                            )
                            print(f"   ✅ Created mapping for '{data['inspector_name']}'")
                        except Exception as e:
                            print(f"   ❌ Error creating mapping: {e}")
        
        # Test filtering logic
        print(f"\n🧪 Testing Filtering Logic:")
        
        # Get base inspections
        four_months_ago = datetime.now() - timedelta(days=120)
        inspections = FoodSafetyAgencyInspection.objects.filter(date_of_inspection__gte=four_months_ago)
        print(f"   Base inspections (last 4 months): {inspections.count()}")
        
        # Try to find inspector mapping again
        inspector_id = None
        try:
            # Try by full name first
            full_name = percy_user.get_full_name()
            if full_name:
                mapping = InspectorMapping.objects.get(inspector_name=full_name)
                inspector_id = mapping.inspector_id
                print(f"   ✅ Found mapping by full name: ID {inspector_id}")
        except InspectorMapping.DoesNotExist:
            try:
                # Try by username
                mapping = InspectorMapping.objects.get(inspector_name=percy_user.username)
                inspector_id = mapping.inspector_id
                print(f"   ✅ Found mapping by username: ID {inspector_id}")
            except InspectorMapping.DoesNotExist:
                print(f"   ❌ No mapping found at all")
        
        if inspector_id:
            # Filter inspections
            percy_inspections = inspections.filter(inspector_id=inspector_id)
            print(f"   Percy's inspections: {percy_inspections.count()}")
            
            if percy_inspections.exists():
                print(f"   ✅ Percy should see {percy_inspections.count()} inspections")
                
                # Show sample inspections
                sample_inspections = percy_inspections[:3]
                for insp in sample_inspections:
                    print(f"      - {insp.client_name} on {insp.date_of_inspection}")
            else:
                print(f"   ❌ No inspections found for Percy's inspector ID")
        else:
            print(f"   ❌ No inspector ID found - Percy will see 0 inspections")
        
    except User.DoesNotExist:
        print(f"❌ Percy user account not found")

if __name__ == "__main__":
    try:
        debug_percy_access()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
