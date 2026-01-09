#!/usr/bin/env python
"""
Test script to verify SQL Server product name fetching
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import fetch_product_names_for_inspection
from main.models import FoodSafetyAgencyInspection

def test_product_name_fetching():
    """Test fetching product names from SQL Server"""
    print("=" * 80)
    print("TESTING SQL SERVER PRODUCT NAME FETCHING")
    print("=" * 80)
    
    # Get a few test inspections
    test_inspections = FoodSafetyAgencyInspection.objects.all()[:5]
    
    for inspection in test_inspections:
        print(f"\n🔍 Testing inspection {inspection.remote_id}:")
        print(f"   Client: {inspection.client_name}")
        print(f"   Date: {inspection.date_of_inspection}")
        print(f"   Current product name: {inspection.product_name or 'None'}")
        
        try:
            # Test fetching product names
            sql_product_names = fetch_product_names_for_inspection(
                inspection_id=inspection.remote_id,
                client_name=inspection.client_name,
                inspection_date=inspection.date_of_inspection
            )
            
            if sql_product_names:
                print(f"   ✅ Found {len(sql_product_names)} product names from SQL Server:")
                for i, name in enumerate(sql_product_names, 1):
                    print(f"      {i}. {name}")
            else:
                print(f"   ❌ No product names found in SQL Server")
                
        except Exception as e:
            print(f"   ❌ Error fetching product names: {e}")
    
    print("\n" + "=" * 80)
    print("TESTING SPECIFIC INSPECTION IDS")
    print("=" * 80)
    
    # Test specific inspection IDs that we know exist
    test_ids = [8905, 8896, 8897, 8900]
    
    for inspection_id in test_ids:
        print(f"\n🔍 Testing inspection ID {inspection_id}:")
        try:
            sql_product_names = fetch_product_names_for_inspection(inspection_id=inspection_id)
            
            if sql_product_names:
                print(f"   ✅ Found {len(sql_product_names)} product names:")
                for i, name in enumerate(sql_product_names, 1):
                    print(f"      {i}. {name}")
            else:
                print(f"   ❌ No product names found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_product_name_fetching()
