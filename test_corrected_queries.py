#!/usr/bin/env python
"""
Test the corrected SQL Server queries
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import fetch_product_names_for_inspection

def test_corrected_queries():
    """Test the corrected SQL Server queries"""
    print("=" * 80)
    print("TESTING CORRECTED SQL SERVER QUERIES")
    print("=" * 80)
    
    # Test with some inspection IDs that should have data
    test_ids = [1, 2, 3]  # These should have data based on our debug output
    
    for inspection_id in test_ids:
        print(f"\n🔍 Testing inspection ID {inspection_id}:")
        try:
            product_names = fetch_product_names_for_inspection(inspection_id=inspection_id)
            
            if product_names:
                print(f"   ✅ SUCCESS: Found {len(product_names)} product names:")
                for i, name in enumerate(product_names, 1):
                    print(f"      {i}. {name}")
            else:
                print(f"   ℹ️  No product names found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎯 TESTING COMPLETE!")
    print(f"   If you see product names above, the system is working!")
    print(f"   Refresh your browser to see the changes in the UI.")

if __name__ == "__main__":
    test_corrected_queries()
