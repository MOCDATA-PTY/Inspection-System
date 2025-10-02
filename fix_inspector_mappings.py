#!/usr/bin/env python3
"""
Create InspectorMapping records for all inspector users
This fixes the issue where inspectors can't see their inspections
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

def fix_inspector_mappings():
    """Create InspectorMapping records for all inspector users"""
    print("🔗 Creating Inspector Mappings")
    print("=" * 60)
    
    from django.contrib.auth import get_user_model
    from main.models import InspectorMapping, FoodSafetyAgencyInspection
    
    User = get_user_model()
    
    # Get all inspector users
    inspector_users = User.objects.filter(role='inspector')
    print(f"👥 Found {len(inspector_users)} inspector users")
    
    # Get all unique inspector data from inspections
    inspector_data = FoodSafetyAgencyInspection.objects.values(
        'inspector_name', 'inspector_id'
    ).distinct().exclude(
        inspector_name__isnull=True
    ).exclude(
        inspector_name=''
    ).exclude(
        inspector_name='Unknown'
    )
    
    print(f"📊 Found {len(inspector_data)} unique inspectors in inspection data\n")
    
    created_count = 0
    updated_count = 0
    
    for user in inspector_users:
        # Skip non-inspector accounts
        if user.username in ['admin', 'test_inspector']:
            continue
            
        full_name = f"{user.first_name} {user.last_name}".strip()
        
        print(f"🔍 Processing user: {user.username} ({full_name})")
        
        # Find matching inspector data
        matching_inspector = None
        for inspector in inspector_data:
            if inspector['inspector_name'] == full_name:
                matching_inspector = inspector
                break
        
        if matching_inspector:
            inspector_id = matching_inspector['inspector_id']
            inspector_name = matching_inspector['inspector_name']
            
            try:
                # Check if mapping already exists
                mapping, created = InspectorMapping.objects.get_or_create(
                    inspector_name=inspector_name,
                    defaults={
                        'inspector_id': inspector_id,
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"   ✅ Created mapping: {inspector_name} → ID {inspector_id}")
                else:
                    # Update existing mapping
                    mapping.inspector_id = inspector_id
                    mapping.is_active = True
                    mapping.save()
                    updated_count += 1
                    print(f"   🔄 Updated mapping: {inspector_name} → ID {inspector_id}")
                    
                # Check how many inspections this inspector has
                inspection_count = FoodSafetyAgencyInspection.objects.filter(
                    inspector_id=inspector_id
                ).count()
                print(f"      📊 Has {inspection_count} inspections")
                
            except Exception as e:
                print(f"   ❌ Error creating mapping for {inspector_name}: {e}")
        else:
            print(f"   ⚠️ No matching inspector data found for {full_name}")
        
        print()
    
    print("=" * 60)
    print("📈 MAPPING CREATION SUMMARY")
    print("=" * 60)
    print(f"✅ Created: {created_count} new mappings")
    print(f"🔄 Updated: {updated_count} existing mappings")
    
    # Show all mappings
    print(f"\n🔗 ALL INSPECTOR MAPPINGS:")
    print("-" * 50)
    
    mappings = InspectorMapping.objects.all().order_by('inspector_name')
    for mapping in mappings:
        inspection_count = FoodSafetyAgencyInspection.objects.filter(
            inspector_id=mapping.inspector_id
        ).count()
        
        print(f"👤 {mapping.inspector_name}")
        print(f"   ID: {mapping.inspector_id}")
        print(f"   Active: {'Yes' if mapping.is_active else 'No'}")
        print(f"   Inspections: {inspection_count}")
        print()

def test_inspector_access():
    """Test if Percy Maleka can now see inspections"""
    print("\n🧪 Testing Inspector Access")
    print("=" * 60)
    
    from main.models import InspectorMapping, FoodSafetyAgencyInspection
    
    # Test Percy Maleka specifically
    percy_name = "PERCY MALEKA"
    
    try:
        # Find Percy's mapping
        percy_mapping = InspectorMapping.objects.get(inspector_name=percy_name)
        print(f"✅ Found mapping for {percy_name}")
        print(f"   Inspector ID: {percy_mapping.inspector_id}")
        print(f"   Active: {percy_mapping.is_active}")
        
        # Count Percy's inspections
        percy_inspections = FoodSafetyAgencyInspection.objects.filter(
            inspector_id=percy_mapping.inspector_id
        )
        
        total_count = percy_inspections.count()
        recent_count = percy_inspections.filter(date_of_inspection__gte='2025-07-01').count()
        
        print(f"   Total Inspections: {total_count}")
        print(f"   Recent Inspections (since July 2025): {recent_count}")
        
        if recent_count > 0:
            print(f"   ✅ Percy should now be able to see {recent_count} recent inspections")
        else:
            print(f"   ⚠️ Percy has no recent inspections in the 4-month window")
            
    except InspectorMapping.DoesNotExist:
        print(f"❌ No mapping found for {percy_name}")
        
        # Check if Percy exists in inspection data
        percy_inspections = FoodSafetyAgencyInspection.objects.filter(
            inspector_name=percy_name
        )
        if percy_inspections.exists():
            percy_data = percy_inspections.values('inspector_id').distinct().first()
            print(f"   Found in inspections with ID: {percy_data['inspector_id']}")
        else:
            print(f"   Not found in inspection data either")

if __name__ == "__main__":
    try:
        fix_inspector_mappings()
        test_inspector_access()
        
        print("\n🎉 Inspector mapping fix completed!")
        print("📝 Percy Maleka and other inspectors should now see their inspections")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
