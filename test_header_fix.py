#!/usr/bin/env python
"""
Test script to verify CSS header fixes are working
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def test_header_fix():
    """Test if the header fix CSS is being applied correctly"""
    print("=" * 80)
    print("TESTING HEADER FIX CSS")
    print("=" * 80)
    
    # Create a test client
    client = Client()
    
    # Try to access the shipments page
    try:
        # First, let's check if we can access the page
        response = client.get('/shipments/')
        print(f"📊 Page access status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Page loads successfully")
            
            # Check if our CSS rules are in the response
            content = response.content.decode('utf-8')
            
            # Check for specific CSS rules we added
            css_checks = [
                ('position: sticky', 'Sticky positioning'),
                ('z-index: 10', 'Z-index for headers'),
                ('table-layout: fixed', 'Fixed table layout'),
                ('box-sizing: border-box', 'Box sizing'),
                ('col-km.*width: 120px', 'KM column width'),
                ('col-hours.*width: 120px', 'Hours column width'),
            ]
            
            print("\n🔍 Checking CSS rules:")
            for pattern, description in css_checks:
                if pattern in content:
                    print(f"   ✅ {description}: Found")
                else:
                    print(f"   ❌ {description}: Missing")
            
            # Check if the template is being used
            if 'shipment_list_clean.html' in content or 'shipmentsTable' in content:
                print("✅ Template is being used")
            else:
                print("❌ Template not found")
                
        else:
            print(f"❌ Page access failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing page: {e}")
    
    print("\n" + "=" * 80)
    print("CSS VERIFICATION COMPLETE")
    print("=" * 80)
    print("If CSS rules are missing, the browser cache might need clearing.")
    print("Try: Ctrl+Shift+R (hard refresh) or clear browser cache.")

if __name__ == "__main__":
    test_header_fix()
