#!/usr/bin/env python
"""
Test script to verify the template fix for compliance status.
This simulates exactly what the template will show after the fix.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

def test_template_fix():
    """Test the template fix for specific Boxer inspections from the UI"""
    print("=" * 80)
    print("TEMPLATE FIX VERIFICATION")
    print("=" * 80)
    
    # Test the specific inspections from the UI that should show different compliance
    test_cases = [
        {'id': 8905, 'expected': 'Non-Compliant', 'client': 'Boxer Superstore - Kwamashu 2'},
        {'id': 8904, 'expected': 'Compliant', 'client': 'Boxer Superstore - Kwamashu 2'},
        {'id': 8817, 'expected': 'Non-Compliant', 'client': 'Boxer Superstore Phola Park'},
        {'id': 8818, 'expected': 'Compliant', 'client': 'Boxer Superstore Phola Park'},
    ]
    
    print("🧪 Testing specific cases from UI:")
    print("-" * 80)
    
    for case in test_cases:
        try:
            inspection = FoodSafetyAgencyInspection.objects.get(remote_id=case['id'])
            
            # Simulate the template logic (AFTER the fix)
            if inspection.is_direction_present_for_this_inspection:
                template_result = 'Non-Compliant'
                css_class = 'compliance-status non-compliant'
                title = 'Non-Compliant (Direction Present)'
            else:
                template_result = 'Compliant'
                css_class = 'compliance-status compliant'
                title = 'Compliant (No Direction)'
            
            # Check if it matches expected
            status = "✅ CORRECT" if template_result == case['expected'] else "❌ WRONG"
            
            print(f"ID {case['id']}: {case['client']}")
            print(f"  Direction Present: {inspection.is_direction_present_for_this_inspection}")
            print(f"  Expected: {case['expected']}")
            print(f"  Template Shows: {template_result}")
            print(f"  CSS Class: {css_class}")
            print(f"  Status: {status}")
            print("-" * 40)
            
        except FoodSafetyAgencyInspection.DoesNotExist:
            print(f"❌ ID {case['id']}: Not found in database")
            print("-" * 40)
    
    # Show a broader sample to demonstrate the fix
    print(f"\n📊 BROADER SAMPLE (First 10 Boxer inspections):")
    print("-" * 80)
    
    boxer_inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains='Boxer'
    ).order_by('-remote_id')[:10]
    
    compliant_count = 0
    non_compliant_count = 0
    
    for inspection in boxer_inspections:
        # Simulate template logic
        if inspection.is_direction_present_for_this_inspection:
            template_result = 'Non-Compliant'
            non_compliant_count += 1
            icon = "🔴"
        else:
            template_result = 'Compliant'
            compliant_count += 1
            icon = "🟢"
        
        print(f"{icon} ID {inspection.remote_id}: {inspection.client_name[:30]}... | {template_result}")
    
    print(f"\n📈 SAMPLE SUMMARY:")
    print(f"  🟢 Compliant: {compliant_count}")
    print(f"  🔴 Non-Compliant: {non_compliant_count}")
    print(f"  📊 Total: {compliant_count + non_compliant_count}")
    
    if non_compliant_count > 0:
        print(f"\n✅ SUCCESS: Template fix will show both compliant AND non-compliant inspections!")
    else:
        print(f"\n⚠️  WARNING: No non-compliant inspections in this sample.")

if __name__ == "__main__":
    print("🚀 Testing template fix for compliance status...\n")
    test_template_fix()
    print(f"\n🏁 Template fix verification completed!")
