#!/usr/bin/env python
"""
Test script to verify JavaScript header fix is working
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def test_js_fix():
    """Test if the JavaScript header fix is in the template"""
    print("=" * 80)
    print("TESTING JAVASCRIPT HEADER FIX")
    print("=" * 80)
    
    # Read the template file
    template_path = "main/templates/main/shipment_list_clean.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for JavaScript functions we added
        js_checks = [
            ('setupHeaderPositionFix', 'Header position fix setup function'),
            ('fixHeaderPositions', 'Header position fix function'),
            ('expand-btn.*click', 'Expand button click handler'),
            ('position.*sticky', 'Sticky positioning'),
            ('zIndex.*100', 'Z-index for headers'),
            ('col-km.*120px', 'KM column width fix'),
            ('col-hours.*120px', 'Hours column width fix'),
        ]
        
        print("🔍 Checking JavaScript functions:")
        for pattern, description in js_checks:
            if pattern in content:
                print(f"   ✅ {description}: Found")
            else:
                print(f"   ❌ {description}: Missing")
        
        # Check if the function is called on DOM ready
        if 'setupHeaderPositionFix()' in content:
            print("   ✅ Function is called on DOM ready")
        else:
            print("   ❌ Function not called on DOM ready")
            
        print(f"\n📊 Template file size: {len(content)} characters")
        print(f"📊 Template file lines: {len(content.splitlines())} lines")
        
    except Exception as e:
        print(f"❌ Error reading template: {e}")
    
    print("\n" + "=" * 80)
    print("JAVASCRIPT VERIFICATION COMPLETE")
    print("=" * 80)
    print("If functions are found, the JavaScript fix should work.")
    print("Check browser console for 'Header positions fixed' message when expanding.")

if __name__ == "__main__":
    test_js_fix()
