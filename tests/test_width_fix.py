#!/usr/bin/env python
"""
Test script to verify width constraint fixes for detail table
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def test_width_fix():
    """Test if the width constraint fixes are in the template"""
    print("=" * 80)
    print("TESTING WIDTH CONSTRAINT FIXES")
    print("=" * 80)
    
    # Read the template file
    template_path = "main/templates/main/shipment_list_clean.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for width constraint fixes
        width_checks = [
            ('min-width: 100%', 'Detail table min-width constraint'),
            ('max-width: 100%', 'Detail table max-width constraint'),
            ('calc(100vw - 100px)', 'Detail wrapper viewport constraint'),
            ('overflow: hidden', 'Detail row overflow constraint'),
            ('overflow: visible', 'Main table overflow setting'),
            ('detail-table.*maxWidth.*100%', 'JavaScript width constraint'),
            ('detail-table-wrapper.*maxWidth', 'JavaScript wrapper constraint'),
        ]
        
        print("🔍 Checking width constraint fixes:")
        for pattern, description in width_checks:
            if pattern in content:
                print(f"   ✅ {description}: Found")
            else:
                print(f"   ❌ {description}: Missing")
        
        # Check if the old problematic width is removed
        if 'min-width: 1560px' in content:
            print("   ⚠️  Old problematic width (1560px) still present")
        else:
            print("   ✅ Old problematic width (1560px) removed")
            
        print(f"\n📊 Template file size: {len(content)} characters")
        print(f"📊 Template file lines: {len(content.splitlines())} lines")
        
    except Exception as e:
        print(f"❌ Error reading template: {e}")
    
    print("\n" + "=" * 80)
    print("WIDTH CONSTRAINT VERIFICATION COMPLETE")
    print("=" * 80)
    print("✅ If all checks pass, the detail table should no longer push main headers around.")
    print("🔄 The detail table will now scroll horizontally within its container.")
    print("📱 Main table headers should stay in place when expanding inspections.")

if __name__ == "__main__":
    test_width_fix()
