#!/usr/bin/env python3
"""
Simple test to check template rendering
"""

import requests
import time

def test_simple():
    """Simple test to check what's being rendered"""
    print("🔍 Testing simple template rendering...")
    
    # Wait a moment for server to start
    time.sleep(2)
    
    try:
        # Make request to inspections page
        response = requests.get('http://127.0.0.1:8000/inspections/', timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        
        # Look for specific patterns in the HTML
        content = response.text
        
        # Check for table structure
        if '<table id="shipmentsTable">' in content:
            print("✅ Table structure found")
        else:
            print("❌ Table structure NOT found")
            
        # Check for tbody
        if '<tbody>' in content:
            print("✅ tbody found")
        else:
            print("❌ tbody NOT found")
            
        # Check for any error messages
        if 'error' in content.lower():
            print("❌ Error messages found in content")
            # Find error messages
            import re
            error_matches = re.findall(r'error[^<]*', content, re.I)
            for match in error_matches[:3]:
                print(f"    {match}")
        
        # Check for shipments loop
        if '{% for shipment in shipments %}' in content:
            print("✅ Template loop found")
        else:
            print("❌ Template loop NOT found")
            
        # Check if there's any actual data
        if 'group-row' in content:
            print("✅ Group rows found")
        else:
            print("❌ No group rows found")
            
        # Check for any debug output
        if 'DEBUG' in content or 'debug' in content:
            print("🔍 Debug output found")
            # Extract debug lines
            import re
            debug_lines = re.findall(r'[^<]*DEBUG[^<]*', content, re.I)
            for line in debug_lines[:5]:
                print(f"    {line.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_simple()
