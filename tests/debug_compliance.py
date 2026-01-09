#!/usr/bin/env python
"""
Debug script to check why inspection 8905 is showing as compliant when it should be non-compliant.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

def debug_inspection_8905():
    """Debug the specific inspection that should be non-compliant"""
    print("=" * 60)
    print("DEBUGGING INSPECTION 8905")
    print("=" * 60)
    
    try:
        inspection = FoodSafetyAgencyInspection.objects.get(remote_id=8905)
        
        print(f"Inspection Details:")
        print(f"  Remote ID: {inspection.remote_id}")
        print(f"  Client: {inspection.client_name}")
        print(f"  Commodity: {inspection.commodity}")
        print(f"  is_direction_present_for_this_inspection: {inspection.is_direction_present_for_this_inspection}")
        print(f"  Type: {type(inspection.is_direction_present_for_this_inspection)}")
        
        # Check all direction-related fields
        print(f"\nAll direction/compliance related fields:")
        for field in inspection._meta.get_fields():
            if 'direction' in field.name.lower() or 'compliance' in field.name.lower():
                try:
                    value = getattr(inspection, field.name)
                    print(f"  {field.name}: {value} (type: {type(value)})")
                except:
                    print(f"  {field.name}: <unable to read>")
        
        # Template simulation
        print(f"\nTemplate Logic Simulation:")
        if inspection.is_direction_present_for_this_inspection:
            template_result = "Non-Compliant"
            css_class = "compliance-status non-compliant"
        else:
            template_result = "Compliant"
            css_class = "compliance-status compliant"
        
        print(f"  Template should show: {template_result}")
        print(f"  CSS class: {css_class}")
        
        # Check if there are any other issues
        print(f"\nAdditional Debug Info:")
        print(f"  Database record exists: Yes")
        print(f"  Field value is boolean: {isinstance(inspection.is_direction_present_for_this_inspection, bool)}")
        print(f"  Field value is truthy: {bool(inspection.is_direction_present_for_this_inspection)}")
        
    except FoodSafetyAgencyInspection.DoesNotExist:
        print("❌ Inspection 8905 not found!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def check_filter_results():
    """Check what the filter should return"""
    print(f"\n" + "=" * 60)
    print("CHECKING FILTER RESULTS")
    print("=" * 60)
    
    # Simulate the filter from the view
    non_compliant = FoodSafetyAgencyInspection.objects.filter(
        is_direction_present_for_this_inspection=True
    )
    
    print(f"Non-compliant inspections count: {non_compliant.count()}")
    
    # Check if 8905 is in the results
    inspection_8905_in_results = non_compliant.filter(remote_id=8905).exists()
    print(f"Inspection 8905 in non-compliant results: {inspection_8905_in_results}")
    
    if inspection_8905_in_results:
        print("✅ Filter is working correctly - 8905 should appear in non-compliant filter")
    else:
        print("❌ Filter issue - 8905 is not being returned by non-compliant filter")
    
    # Show first few results
    print(f"\nFirst 5 non-compliant inspections:")
    for i, inspection in enumerate(non_compliant[:5], 1):
        print(f"  {i}. ID {inspection.remote_id}: {inspection.client_name} | Direction: {inspection.is_direction_present_for_this_inspection}")

if __name__ == "__main__":
    print("🔍 Debugging compliance display issue...\n")
    debug_inspection_8905()
    check_filter_results()
    print(f"\n🏁 Debug completed!")
