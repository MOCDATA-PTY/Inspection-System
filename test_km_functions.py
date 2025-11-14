#!/usr/bin/env python3
"""
Test script to verify KM and Hours functions are properly defined in the template.
This script checks for syntax errors and function definitions in the HTML template.
"""

import re
import os
from pathlib import Path

def test_km_functions():
    """Test the KM and Hours functions in the template file."""
    
    template_path = Path("main/templates/main/shipment_list_clean.html")
    
    if not template_path.exists():
        print("❌ Template file not found:", template_path)
        return False
    
    print("🔍 Testing KM and Hours functions in template...")
    print(f"📁 Template path: {template_path}")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False
    
    # Test 1: Check for syntax errors in script tags
    print("\n🧪 Test 1: Checking for script syntax errors...")
    
    # Find all script sections
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)
    
    print(f"📊 Found {len(scripts)} script sections")
    
    syntax_errors = []
    for i, script in enumerate(scripts):
        # Check for common syntax errors
        if script.count('{') != script.count('}'):
            syntax_errors.append(f"Script {i+1}: Unmatched braces")
        
        if script.count('(') != script.count(')'):
            syntax_errors.append(f"Script {i+1}: Unmatched parentheses")
        
        # Check for incomplete function definitions
        if 'function(' in script and not script.strip().endswith('}'):
            syntax_errors.append(f"Script {i+1}: Incomplete function definition")
    
    if syntax_errors:
        print("❌ Syntax errors found:")
        for error in syntax_errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ No syntax errors found in script sections")
    
    # Test 2: Check for KM function definitions
    print("\n🧪 Test 2: Checking KM function definitions...")
    
    km_patterns = [
        r'window\.updateGroupKmTraveled\s*=',
        r'window\._fullUpdateGroupKmTraveled\s*=',
        r'function\s+updateGroupKmTraveled\s*\(',
        r'updateGroupKmTraveled\s*\(this\)'
    ]
    
    km_found = []
    for pattern in km_patterns:
        matches = re.findall(pattern, content)
        if matches:
            km_found.append(f"✅ Found: {pattern} ({len(matches)} matches)")
        else:
            km_found.append(f"❌ Missing: {pattern}")
    
    for result in km_found:
        print(f"   {result}")
    
    # Test 3: Check for Hours function definitions
    print("\n🧪 Test 3: Checking Hours function definitions...")
    
    hours_patterns = [
        r'window\.updateGroupHours\s*=',
        r'window\._fullUpdateGroupHours\s*=',
        r'function\s+updateGroupHours\s*\(',
        r'updateGroupHours\s*\(this\)'
    ]
    
    hours_found = []
    for pattern in hours_patterns:
        matches = re.findall(pattern, content)
        if matches:
            hours_found.append(f"✅ Found: {pattern} ({len(matches)} matches)")
        else:
            hours_found.append(f"❌ Missing: {pattern}")
    
    for result in hours_found:
        print(f"   {result}")
    
    # Test 4: Check for early placeholder functions
    print("\n🧪 Test 4: Checking early placeholder functions...")
    
    early_patterns = [
        r'Early definition of updateGroupKmTraveled',
        r'Early definition of updateGroupHours',
        r'window\._pendingKmUpdates',
        r'window\._pendingHoursUpdates'
    ]
    
    early_found = []
    for pattern in early_patterns:
        matches = re.findall(pattern, content)
        if matches:
            early_found.append(f"✅ Found: {pattern} ({len(matches)} matches)")
        else:
            early_found.append(f"❌ Missing: {pattern}")
    
    for result in early_found:
        print(f"   {result}")
    
    # Test 5: Check for console.log statements
    print("\n🧪 Test 5: Checking debug logging...")
    
    log_patterns = [
        r'console\.log.*Full.*function.*loaded.*active',
        r'console\.log.*Function type check',
        r'console\.log.*Early.*called.*function not fully loaded'
    ]
    
    log_found = []
    for pattern in log_patterns:
        matches = re.findall(pattern, content)
        if matches:
            log_found.append(f"✅ Found: {pattern} ({len(matches)} matches)")
        else:
            log_found.append(f"❌ Missing: {pattern}")
    
    for result in log_found:
        print(f"   {result}")
    
    # Test 6: Check for CSRF token handling
    print("\n🧪 Test 6: Checking CSRF token handling...")
    
    csrf_patterns = [
        r'getCSRFToken\s*\(',
        r'csrfmiddlewaretoken',
        r'CSRF token set globally'
    ]
    
    csrf_found = []
    for pattern in csrf_patterns:
        matches = re.findall(pattern, content)
        if matches:
            csrf_found.append(f"✅ Found: {pattern} ({len(matches)} matches)")
        else:
            csrf_found.append(f"❌ Missing: {pattern}")
    
    for result in csrf_found:
        print(f"   {result}")
    
    # Summary
    print("\n📊 Test Summary:")
    total_tests = 6
    passed_tests = 0
    
    if not syntax_errors:
        passed_tests += 1
        print("✅ Script syntax: PASSED")
    else:
        print("❌ Script syntax: FAILED")
    
    if any("✅ Found" in result for result in km_found):
        passed_tests += 1
        print("✅ KM functions: PASSED")
    else:
        print("❌ KM functions: FAILED")
    
    if any("✅ Found" in result for result in hours_found):
        passed_tests += 1
        print("✅ Hours functions: PASSED")
    else:
        print("❌ Hours functions: FAILED")
    
    if any("✅ Found" in result for result in early_found):
        passed_tests += 1
        print("✅ Early placeholders: PASSED")
    else:
        print("❌ Early placeholders: FAILED")
    
    if any("✅ Found" in result for result in log_found):
        passed_tests += 1
        print("✅ Debug logging: PASSED")
    else:
        print("❌ Debug logging: FAILED")
    
    if any("✅ Found" in result for result in csrf_found):
        passed_tests += 1
        print("✅ CSRF handling: PASSED")
    else:
        print("❌ CSRF handling: FAILED")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! KM and Hours functions should be working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        return False

def test_endpoint_availability():
    """Test if the required endpoints exist."""
    print("\n🧪 Testing endpoint availability...")
    
    # Check for Django URL patterns
    urls_path = Path("main/urls.py")
    if urls_path.exists():
        try:
            with open(urls_path, 'r', encoding='utf-8') as f:
                urls_content = f.read()
            
            endpoints = [
                'update-group-km-traveled',
                'update-group-hours'
            ]
            
            for endpoint in endpoints:
                if endpoint in urls_content:
                    print(f"✅ Endpoint found: {endpoint}")
                else:
                    print(f"❌ Endpoint missing: {endpoint}")
                    
        except Exception as e:
            print(f"❌ Error reading URLs file: {e}")
    else:
        print("❌ URLs file not found")

if __name__ == "__main__":
    print("🚀 Starting KM Functions Test Suite")
    print("=" * 50)
    
    success = test_km_functions()
    test_endpoint_availability()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test completed successfully!")
        print("💡 The KM and Hours functions should be working in your application.")
    else:
        print("❌ Test completed with issues.")
        print("💡 Check the errors above and fix them in the template.")
    
    print("\n🔧 Next steps:")
    print("1. Refresh your browser to reload the template")
    print("2. Check the browser console for the debug messages")
    print("3. Try entering values in the KM and Hours fields")
    print("4. Look for the '✅ Full function loaded and active' messages")
