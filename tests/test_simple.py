#!/usr/bin/env python3
"""
Simple test to verify email functions are working.
"""

import os
import sys
from pathlib import Path

def test_simple_email_functions():
    """Test if email functions are defined correctly."""
    
    html_file = Path("main/templates/main/shipment_list_clean.html")
    
    if not html_file.exists():
        print("❌ HTML file not found!")
        return False
    
    print("🔍 Simple Email Functions Test")
    print("=" * 40)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Check if functions are defined
    print("\n📋 Test 1: Function Definitions")
    
    functions = [
        'window.updateGroupAdditionalEmails = function(input)',
        'window.addEmailInput = function(button)',
        'window.removeEmailInput = function(button)'
    ]
    
    all_defined = True
    for func in functions:
        if func in content:
            print(f"✅ Found: {func}")
        else:
            print(f"❌ Missing: {func}")
            all_defined = False
    
    # Test 2: Check if functions are called in HTML
    print("\n📋 Test 2: HTML Function Calls")
    
    html_calls = [
        'onchange="updateGroupAdditionalEmails(this)"',
        'onclick="addEmailInput(this)"',
        'onclick="removeEmailInput(this)"'
    ]
    
    all_calls_found = True
    for call in html_calls:
        count = content.count(call)
        if count > 0:
            print(f"✅ Found {count} instances of: {call}")
        else:
            print(f"❌ Not found: {call}")
            all_calls_found = False
    
    # Test 3: Check for basic syntax
    print("\n📋 Test 3: Basic Syntax Check")
    
    syntax_ok = True
    
    # Check for the specific error we fixed
    if '};);' in content:
        print("❌ Found '};);' syntax error")
        syntax_ok = False
    else:
        print("✅ No '};);' syntax error found")
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 SIMPLE TEST RESULTS")
    print("=" * 40)
    
    tests = [
        ("Function Definitions", all_defined),
        ("HTML Function Calls", all_calls_found),
        ("Basic Syntax", syntax_ok)
    ]
    
    passed = 0
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED! Email functions should work correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        return False

def main():
    """Run simple email functions test."""
    
    print("🧪 Simple Email Functions Test")
    print("Testing core functionality...")
    
    try:
        result = test_simple_email_functions()
        if result:
            print("\n🎉 READY FOR BROWSER TESTING!")
            print("Email functions should work correctly now.")
            return 0
        else:
            print("\n⚠️  NOT READY FOR BROWSER TESTING!")
            print("Fix the issues above before testing in browser.")
            return 1
    except Exception as e:
        print(f"❌ Test error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())