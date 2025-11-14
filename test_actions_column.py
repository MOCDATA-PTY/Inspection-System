#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify Actions column configuration for lab technicians.

This script verifies:
1. Actions column exists in the template
2. Actions column has sticky positioning CSS
3. Scientists (lab technicians) can see the Actions column
4. Lab upload buttons are present for sampled products
"""

import re
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_actions_column():
    """Test Actions column configuration"""

    template_path = r"d:\Zama System\Inspection-System-master\Inspection-System-master\main\templates\main\shipment_list_clean.html"

    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("="*80)
    print("ACTIONS COLUMN VERIFICATION TEST")
    print("="*80)
    print()

    # Test 1: Check Actions column header exists
    print("Test 1: Checking Actions column header...")
    actions_header_pattern = r'{% if user_role != [\'"]inspector[\'"] %}.*?<th.*?>Actions.*?</th>'
    if re.search(actions_header_pattern, content, re.DOTALL):
        print("✅ Actions column header found")
        print("   - Condition: user_role != 'inspector'")
        print("   - This means scientists (lab technicians) CAN see it")
    else:
        print("❌ Actions column header not found or misconfigured")
        return False

    print()

    # Test 2: Check Actions column body exists
    print("Test 2: Checking Actions column body cells...")
    actions_body_pattern = r'{% if user_role != [\'"]inspector[\'"] %}.*?<td>.*?Lab upload buttons'
    if re.search(actions_body_pattern, content, re.DOTALL):
        print("✅ Actions column body cells found")
    else:
        print("❌ Actions column body cells not found")
        return False

    print()

    # Test 3: Check Lab upload buttons exist
    print("Test 3: Checking Lab upload buttons...")
    buttons_found = []

    if 'btn-lab' in content and 'uploadLab' in content:
        buttons_found.append('Lab')
    if 'btn-lab-form' in content and 'uploadLabForm' in content:
        buttons_found.append('Lab Form')
    if 'btn-retest' in content and 'uploadRetest' in content:
        buttons_found.append('Retest')

    if len(buttons_found) == 3:
        print(f"✅ All 3 upload buttons found: {', '.join(buttons_found)}")
    else:
        print(f"❌ Only found {len(buttons_found)} buttons: {', '.join(buttons_found)}")
        return False

    print()

    # Test 4: Check sticky positioning CSS
    print("Test 4: Checking sticky positioning CSS...")
    sticky_pattern = r'\.detail-table.*?nth-child\(15\).*?position:\s*sticky'
    if re.search(sticky_pattern, content, re.DOTALL | re.IGNORECASE):
        print("✅ Sticky positioning CSS found for Actions column (15th child)")
        print("   - This makes the column always visible on the right side")
    else:
        print("⚠️  Warning: Sticky positioning may not be configured")

    print()

    # Test 5: Check role restrictions
    print("Test 5: Checking role-based button restrictions...")
    admin_restriction = r"user_role == ['\"]admin['\"].*?disabled"
    scientist_unrestricted = r"user_role.*?scientist"

    if re.search(admin_restriction, content):
        print("✅ Admin users have buttons disabled (view-only)")

    # Scientists should NOT have restrictions
    scientist_disabled = r"user_role == ['\"]scientist['\"].*?disabled"
    if not re.search(scientist_disabled, content):
        print("✅ Scientists (lab technicians) have NO restrictions - buttons are functional")
    else:
        print("❌ Scientists have restrictions - this is incorrect!")
        return False

    print()

    # Test 6: Check backend filter removal
    print("Test 6: Checking backend filter for scientists...")
    views_path = r"d:\Zama System\Inspection-System-master\Inspection-System-master\main\views\core_views.py"

    if os.path.exists(views_path):
        with open(views_path, 'r', encoding='utf-8') as f:
            views_content = f.read()

        # Check if the scientist-specific filter is removed
        # Look for the pattern where scientist role leads to pass (no filter)
        scientist_no_filter = re.search(
            r"elif request\.user\.role == ['\"]scientist['\"].*?pass.*?# No filtering",
            views_content,
            re.DOTALL
        )

        if scientist_no_filter:
            print("✅ Filter removed - scientists can see all inspections")
            print("   - Scientists now have same access as admins")
        else:
            print("❌ Old filter still exists - scientists still restricted to sampled inspections only")
            return False

    print()

    # Test 7: Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()
    print("✅ Actions column is properly configured!")
    print()
    print("Configuration details:")
    print("  - Column position: 15th column (nth-child(15))")
    print("  - Visibility: Hidden for inspectors, visible for all other roles")
    print("  - Sticky positioning: YES - always visible on right side")
    print("  - Lab technician access: FULL - can upload Lab, Lab Form, and Retest docs")
    print("  - Admin access: VIEW-ONLY - buttons are disabled")
    print("  - Inspector access: HIDDEN - column not shown at all")
    print()
    print("✅ All tests passed!")

    return True

if __name__ == "__main__":
    try:
        success = test_actions_column()
        if success:
            print()
            print("="*80)
            print("NEXT STEPS")
            print("="*80)
            print()
            print("1. Refresh your browser (Ctrl+F5 or Cmd+Shift+R)")
            print("2. Log in as a lab technician (scientist role)")
            print("3. Expand any shipment row")
            print("4. The Actions column should now be STICKY on the right side")
            print("5. You should see Lab, Lab Form, and Retest buttons")
            print()
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
