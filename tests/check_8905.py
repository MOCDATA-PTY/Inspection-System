#!/usr/bin/env python
"""
Check inspection 8905 specifically
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

def check_inspection_8905():
    """Check inspection 8905 specifically"""
    print("=" * 60)
    print("CHECKING INSPECTION 8905 SPECIFICALLY")
    print("=" * 60)
    
    try:
        # Get all inspections with remote_id 8905
        inspections = FoodSafetyAgencyInspection.objects.filter(remote_id=8905)
        print(f"Found {inspections.count()} inspections with remote_id 8905")
        
        for i, inspection in enumerate(inspections):
            print(f"\nInspection {i+1}:")
            print(f"  ID: {inspection.id}")
            print(f"  Remote ID: {inspection.remote_id}")
            print(f"  Client: {inspection.client_name}")
            print(f"  Commodity: {inspection.commodity}")
            print(f"  is_direction_present_for_this_inspection: {inspection.is_direction_present_for_this_inspection}")
            print(f"  Date: {inspection.date_of_inspection}")
            print(f"  Inspector: {inspection.inspector_name}")
            
            # Check if this matches what we see in UI
            if inspection.commodity == "RAW" and inspection.client_name == "Boxer Superstore - Kwamashu 2":
                print(f"  ✅ This matches the UI inspection!")
                expected_status = "🔴 NON-COMPLIANT" if inspection.is_direction_present_for_this_inspection else "🟢 COMPLIANT"
                print(f"  Expected UI status: {expected_status}")
            else:
                print(f"  ❌ This doesn't match the UI inspection")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_inspection_8905()
