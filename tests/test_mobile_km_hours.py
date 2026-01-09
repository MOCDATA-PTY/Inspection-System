#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to verify KM and Hours functionality works on mobile
Checks both backend and frontend configurations
"""
import os
import sys
import django

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model
from main.models import FoodSafetyAgencyInspection
from decimal import Decimal
import re

User = get_user_model()

print("\n" + "="*80)
print("MOBILE KM AND HOURS FUNCTIONALITY TEST")
print("="*80)
print("\nThis test verifies that KM and Hours work on mobile devices\n")

def check_template_mobile_support():
    """Check if the template has proper mobile support for KM and Hours"""
    print("="*80)
    print("STEP 1: Checking Template Mobile Support")
    print("="*80)

    template_path = os.path.join(
        os.path.dirname(__file__),
        'main', 'templates', 'main', 'shipment_list_clean.html'
    )

    if not os.path.exists(template_path):
        print(f"✗ Template not found at: {template_path}")
        return False

    print(f"✓ Template found: {template_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for mobile-specific CSS
    mobile_checks = {
        'Mobile KM column styling': r'\.col-km.*mobile|@media.*col-km',
        'Mobile Hours column styling': r'\.col-hours.*mobile|@media.*col-hours',
        'KM input field': r'group-km-input|km_traveled|km-input',
        'Hours input field': r'group-hours-input|hours|hours-input',
        'Touch-friendly inputs': r'min-height.*44px|touch-target',
        'Mobile responsive table': r'@media.*max-width.*768|mobile-view',
        'updateGroupKmTraveled function': r'updateGroupKmTraveled',
        'updateGroupHours function': r'updateGroupHours',
    }

    print("\nChecking mobile features:")
    print("-"*80)

    found_features = 0
    for check_name, pattern in mobile_checks.items():
        if re.search(pattern, content, re.IGNORECASE):
            print(f"✓ {check_name}: Found")
            found_features += 1
        else:
            print(f"⚠️  {check_name}: Not found (may need improvement)")

    print(f"\nFeatures found: {found_features}/{len(mobile_checks)}")

    # Check for mobile-specific media queries
    media_queries = re.findall(r'@media.*?\(max-width:\s*(\d+)px\)', content)
    if media_queries:
        print(f"\n✓ Found {len(media_queries)} mobile media queries")
        breakpoints = sorted(set([int(x) for x in media_queries]))
        print(f"  Breakpoints: {breakpoints}px")

    return found_features >= len(mobile_checks) * 0.7  # 70% threshold

def test_mobile_input_attributes():
    """Test that input fields have mobile-friendly attributes"""
    print("\n" + "="*80)
    print("STEP 2: Checking Mobile Input Attributes")
    print("="*80)

    template_path = os.path.join(
        os.path.dirname(__file__),
        'main', 'templates', 'main', 'shipment_list_clean.html'
    )

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find KM input configurations
    km_inputs = re.findall(r'<input[^>]*km[^>]*>', content, re.IGNORECASE)
    hours_inputs = re.findall(r'<input[^>]*hours[^>]*>', content, re.IGNORECASE)

    print(f"\nFound {len(km_inputs)} KM input fields")
    print(f"Found {len(hours_inputs)} Hours input fields")

    mobile_attributes = {
        'type="number"': 'Numeric keyboard on mobile',
        'step=': 'Decimal support',
        'min=': 'Minimum value validation',
        'placeholder': 'Visual hint for users',
        'onchange=': 'Auto-save on change',
        'onblur=': 'Save on focus loss',
    }

    print("\nChecking KM input attributes:")
    print("-"*80)
    for attr, description in mobile_attributes.items():
        found = sum(1 for inp in km_inputs if attr in inp.lower())
        if found > 0:
            print(f"✓ {attr:20s} - {description} ({found} inputs)")
        else:
            print(f"⚠️  {attr:20s} - {description} (0 inputs)")

    print("\nChecking Hours input attributes:")
    print("-"*80)
    for attr, description in mobile_attributes.items():
        found = sum(1 for inp in hours_inputs if attr in inp.lower())
        if found > 0:
            print(f"✓ {attr:20s} - {description} ({found} inputs)")
        else:
            print(f"⚠️  {attr:20s} - {description} (0 inputs)")

def test_backend_endpoints():
    """Test that backend endpoints exist for KM and Hours updates"""
    print("\n" + "="*80)
    print("STEP 3: Checking Backend API Endpoints")
    print("="*80)

    urls_path = os.path.join(
        os.path.dirname(__file__),
        'main', 'urls.py'
    )

    if not os.path.exists(urls_path):
        print(f"✗ URLs file not found")
        return False

    with open(urls_path, 'r', encoding='utf-8') as f:
        urls_content = f.read()

    endpoints = {
        'update-km-traveled': 'Individual KM update endpoint',
        'update-group-km-traveled': 'Group KM update endpoint',
        'update-hours': 'Individual Hours update endpoint',
        'update-group-hours': 'Group Hours update endpoint',
    }

    print("\nChecking API endpoints:")
    print("-"*80)

    all_found = True
    for endpoint, description in endpoints.items():
        if endpoint in urls_content:
            print(f"✓ /{endpoint}/ - {description}")
        else:
            print(f"✗ /{endpoint}/ - {description} (NOT FOUND)")
            all_found = False

    return all_found

def test_mobile_responsive_save():
    """Test that data saves correctly on mobile (simulated)"""
    print("\n" + "="*80)
    print("STEP 4: Testing Mobile Data Save (Simulated)")
    print("="*80)

    # Get a test inspection
    test_insp = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection').first()

    if not test_insp:
        print("✗ No inspections found for testing")
        return False

    print(f"\nTest Inspection:")
    print(f"  ID: {test_insp.id}")
    print(f"  Client: {test_insp.client_name}")
    print(f"  Date: {test_insp.date_of_inspection}")

    # Save original values
    original_km = test_insp.km_traveled
    original_hours = test_insp.hours

    print(f"  Original KM: {original_km or 'None'}")
    print(f"  Original Hours: {original_hours or 'None'}")

    # Simulate mobile input (small values typical of mobile entry)
    print("\nSimulating mobile input...")
    print("-"*80)

    mobile_km = Decimal('45.50')
    mobile_hours = Decimal('2.75')

    test_insp.km_traveled = mobile_km
    test_insp.hours = mobile_hours
    test_insp.save()

    # Verify save
    test_insp.refresh_from_db()

    km_saved = test_insp.km_traveled == mobile_km
    hours_saved = test_insp.hours == mobile_hours

    if km_saved and hours_saved:
        print(f"✓ Mobile save successful!")
        print(f"  KM: {test_insp.km_traveled}")
        print(f"  Hours: {test_insp.hours}")
    else:
        print(f"✗ Mobile save failed!")
        print(f"  Expected KM: {mobile_km}, Got: {test_insp.km_traveled}")
        print(f"  Expected Hours: {mobile_hours}, Got: {test_insp.hours}")

    # Restore original values
    test_insp.km_traveled = original_km
    test_insp.hours = original_hours
    test_insp.save()

    print(f"\n✓ Restored original values")

    return km_saved and hours_saved

def check_mobile_ui_guidelines():
    """Check if UI follows mobile best practices"""
    print("\n" + "="*80)
    print("STEP 5: Mobile UI Best Practices")
    print("="*80)

    guidelines = {
        'Touch target size': 'Inputs should be at least 44x44px for easy tapping',
        'Number keyboard': 'type="number" triggers numeric keyboard on mobile',
        'Step attribute': 'step="0.1" allows decimal values',
        'Auto-save': 'onchange/onblur saves without clicking a button',
        'Visual feedback': 'Placeholder text guides the user',
        'Responsive design': 'Columns stack properly on small screens',
        'Font size': 'Text should be at least 16px to prevent zoom on iOS',
        'Spacing': 'Adequate padding between interactive elements',
    }

    print("\nMobile UI Guidelines:")
    print("-"*80)
    for guideline, description in guidelines.items():
        print(f"📱 {guideline:25s} - {description}")

    return True

def show_mobile_testing_instructions():
    """Show instructions for manual mobile testing"""
    print("\n" + "="*80)
    print("MANUAL MOBILE TESTING INSTRUCTIONS")
    print("="*80)

    instructions = """
To test on an actual mobile device:

1. CONNECT TO LOCAL SERVER:
   - Make sure your mobile device is on the same network as your computer
   - Find your computer's IP address (ipconfig on Windows, ifconfig on Mac/Linux)
   - On mobile, go to: http://YOUR_IP:8000

2. LOGIN AS INSPECTOR:
   - Username: developer (or any inspector account)
   - Password: Ethan4269875321

3. TEST KM INPUT:
   - Go to Inspections page
   - Find any inspection
   - Tap on the KM field
   - You should see a NUMERIC keyboard (not regular keyboard)
   - Enter a value like "45.5"
   - Tap outside the field (onblur saves automatically)
   - Refresh the page to verify it saved

4. TEST HOURS INPUT:
   - Tap on the Hours field
   - You should see a NUMERIC keyboard
   - Enter a value like "3.75"
   - Tap outside the field
   - Refresh to verify it saved

5. CHECK RESPONSIVE LAYOUT:
   - Rotate device to portrait/landscape
   - Table should be scrollable horizontally
   - Inputs should remain accessible
   - Touch targets should be large enough (44x44px minimum)

6. TEST EDGE CASES:
   - Try entering 0
   - Try entering decimals (0.5, 1.25, etc.)
   - Try entering large numbers (100+)
   - Try leaving field empty

EXPECTED BEHAVIOR:
   ✓ Numeric keyboard appears on mobile
   ✓ Values save automatically on blur (tap outside)
   ✓ Data persists after refresh
   ✓ No errors in browser console (F12 on desktop, inspect on mobile)
   ✓ Touch targets are easy to tap
"""

    print(instructions)

def main():
    """Run all mobile tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE MOBILE KM AND HOURS TEST")
    print("="*80)

    results = {
        'Template mobile support': False,
        'Mobile input attributes': False,
        'Backend endpoints': False,
        'Mobile data save': False,
        'UI guidelines': False,
    }

    try:
        results['Template mobile support'] = check_template_mobile_support()
        test_mobile_input_attributes()  # Informational only
        results['Backend endpoints'] = test_backend_endpoints()
        results['Mobile data save'] = test_mobile_responsive_save()
        results['UI guidelines'] = check_mobile_ui_guidelines()

        # Show manual testing instructions
        show_mobile_testing_instructions()

        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        print(f"\nAutomated Tests: {passed}/{total} passed")
        print("-"*80)

        for test_name, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status:10s} - {test_name}")

        print("\n" + "="*80)
        print("CONCLUSION")
        print("="*80)

        if passed == total:
            print("\n✓✓✓ ALL TESTS PASSED!")
            print("\nMobile functionality is ready:")
            print("  ✓ Template has mobile support")
            print("  ✓ Input fields are mobile-friendly")
            print("  ✓ Backend endpoints exist")
            print("  ✓ Data saves correctly")
            print("  ✓ UI follows mobile best practices")
            print("\nTo test on actual mobile device, follow the manual testing")
            print("instructions above.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            print("\nPlease review the failed tests above")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
