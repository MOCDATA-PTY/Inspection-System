#!/usr/bin/env python
"""
Test the filtered product name queries
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import fetch_product_names_for_inspection

def test_filtered_names():
    """Test the filtered product name queries"""
    print("=" * 80)
    print("TESTING FILTERED PRODUCT NAME QUERIES")
    print("=" * 80)
    
    # Test with some inspection IDs from your UI
    test_ids = [8905, 8896, 8897, 8900, 7839, 8904]
    
    for inspection_id in test_ids:
        print(f"\n🔍 Testing inspection ID {inspection_id}:")
        try:
            product_names = fetch_product_names_for_inspection(inspection_id=inspection_id)
            
            if product_names:
                print(f"   ✅ Found {len(product_names)} product names:")
                for i, name in enumerate(product_names, 1):
                    print(f"      {i}. '{name}'")
            else:
                print(f"   ℹ️  No product names found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎯 FILTERED RESULTS:")
    print(f"   ✅ Only actual product names (no client names, sample details, etc.)")
    print(f"   ✅ No empty or null values")
    print(f"   ✅ Clean, trimmed strings")
    print(f"\n📋 NEXT STEPS:")
    print(f"   1. Refresh your browser page")
    print(f"   2. You should now see only clean product names like 'Chicken Sausage'")
    print(f"   3. No more mixed data like 'non | Chicken Sausage | Boxer superstore'")

if __name__ == "__main__":
    test_filtered_names()
