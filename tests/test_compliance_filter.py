#!/usr/bin/env python
"""
Test script to verify compliance filtering and show both compliant and non-compliant cases.
This will help identify why all inspections are showing as compliant in the UI.
"""

import os
import sys
import django
from django.db import connection

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

def test_compliance_filtering():
    """Test compliance filtering to show both compliant and non-compliant cases"""
    print("=" * 70)
    print("COMPLIANCE FILTERING TEST")
    print("=" * 70)
    
    try:
        # Get all inspections
        all_inspections = FoodSafetyAgencyInspection.objects.all()
        print(f"📊 Total inspections in database: {all_inspections.count()}")
        
        # Filter for compliant inspections (is_direction_present_for_this_inspection = False)
        compliant_inspections = FoodSafetyAgencyInspection.objects.filter(
            is_direction_present_for_this_inspection=False
        )
        
        # Filter for non-compliant inspections (is_direction_present_for_this_inspection = True)
        non_compliant_inspections = FoodSafetyAgencyInspection.objects.filter(
            is_direction_present_for_this_inspection=True
        )
        
        print(f"✅ Compliant inspections: {compliant_inspections.count()}")
        print(f"❌ Non-compliant inspections: {non_compliant_inspections.count()}")
        
        # Show sample compliant inspections
        print(f"\n🟢 SAMPLE COMPLIANT INSPECTIONS:")
        print("-" * 70)
        for i, inspection in enumerate(compliant_inspections[:5], 1):
            print(f"{i}. ID: {inspection.remote_id} | Client: {inspection.client_name} | Direction: {inspection.is_direction_present_for_this_inspection}")
        
        # Show sample non-compliant inspections
        print(f"\n🔴 SAMPLE NON-COMPLIANT INSPECTIONS:")
        print("-" * 70)
        for i, inspection in enumerate(non_compliant_inspections[:5], 1):
            print(f"{i}. ID: {inspection.remote_id} | Client: {inspection.client_name} | Direction: {inspection.is_direction_present_for_this_inspection}")
        
        # Test the template logic on both types
        print(f"\n🧪 TEMPLATE LOGIC VERIFICATION:")
        print("-" * 70)
        
        if compliant_inspections.exists():
            sample_compliant = compliant_inspections.first()
            print(f"Compliant Sample - ID: {sample_compliant.remote_id}")
            print(f"  is_direction_present_for_this_inspection: {sample_compliant.is_direction_present_for_this_inspection}")
            print(f"  Template would show: {'Non-Compliant' if sample_compliant.is_direction_present_for_this_inspection else 'Compliant'}")
        
        if non_compliant_inspections.exists():
            sample_non_compliant = non_compliant_inspections.first()
            print(f"Non-Compliant Sample - ID: {sample_non_compliant.remote_id}")
            print(f"  is_direction_present_for_this_inspection: {sample_non_compliant.is_direction_present_for_this_inspection}")
            print(f"  Template would show: {'Non-Compliant' if sample_non_compliant.is_direction_present_for_this_inspection else 'Compliant'}")
        
        # Check if there's a different field being used
        print(f"\n🔍 FIELD ANALYSIS:")
        print("-" * 70)
        sample_inspection = all_inspections.first()
        if sample_inspection:
            print(f"Sample inspection fields related to direction/compliance:")
            # Check if the inspection has other direction-related fields
            for field in sample_inspection._meta.get_fields():
                if 'direction' in field.name.lower() or 'compliance' in field.name.lower():
                    try:
                        value = getattr(sample_inspection, field.name)
                        print(f"  {field.name}: {value}")
                    except:
                        print(f"  {field.name}: <unable to read>")
        
        return compliant_inspections.count(), non_compliant_inspections.count()
        
    except Exception as e:
        print(f"❌ Error during compliance filtering test: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0, 0

def test_boxer_specific():
    """Test Boxer-specific inspections since that's what's shown in the UI"""
    print(f"\n" + "=" * 70)
    print("BOXER SUPERSTORE SPECIFIC TEST")
    print("=" * 70)
    
    try:
        # Filter for Boxer Superstore inspections
        boxer_inspections = FoodSafetyAgencyInspection.objects.filter(
            client_name__icontains='Boxer'
        )
        
        print(f"📊 Total Boxer inspections: {boxer_inspections.count()}")
        
        # Check compliance for Boxer inspections
        boxer_compliant = boxer_inspections.filter(is_direction_present_for_this_inspection=False)
        boxer_non_compliant = boxer_inspections.filter(is_direction_present_for_this_inspection=True)
        
        print(f"✅ Boxer compliant: {boxer_compliant.count()}")
        print(f"❌ Boxer non-compliant: {boxer_non_compliant.count()}")
        
        # Show specific examples from the UI data
        print(f"\n🎯 SPECIFIC BOXER EXAMPLES FROM UI:")
        print("-" * 70)
        
        # Look for the specific inspections mentioned in the UI
        specific_ids = [8905, 8904, 8876, 8817, 8818, 8800]  # From the UI data
        
        for remote_id in specific_ids:
            try:
                inspection = FoodSafetyAgencyInspection.objects.get(remote_id=remote_id)
                template_result = 'Non-Compliant' if inspection.is_direction_present_for_this_inspection else 'Compliant'
                print(f"ID {remote_id}: {inspection.client_name} | Direction: {inspection.is_direction_present_for_this_inspection} | Shows: {template_result}")
            except FoodSafetyAgencyInspection.DoesNotExist:
                print(f"ID {remote_id}: Not found in database")
        
    except Exception as e:
        print(f"❌ Error during Boxer test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting compliance filtering tests...\n")
    
    # Test general compliance filtering
    compliant_count, non_compliant_count = test_compliance_filtering()
    
    # Test Boxer-specific cases
    test_boxer_specific()
    
    print(f"\n🏁 Test completed!")
    print(f"📊 Final Summary: {compliant_count} compliant, {non_compliant_count} non-compliant")
    
    if non_compliant_count == 0:
        print("⚠️  WARNING: No non-compliant inspections found! This might explain why UI shows all as compliant.")
    else:
        print("✅ Both compliant and non-compliant inspections exist in database.")
