#!/usr/bin/env python3
"""
Test script to verify email management functions are working correctly
in the inspection system.
"""

import os
import re
import sys
from pathlib import Path

def test_email_functions_in_html():
    """Test that email functions are properly defined in the HTML file."""
    
    html_file = Path("main/templates/main/shipment_list_clean.html")
    
    if not html_file.exists():
        print("❌ HTML file not found!")
        return False
    
    print("🔍 Testing email functions in HTML file...")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for email function definitions
    email_functions = [
        'window.updateGroupAdditionalEmails',
        'window.addEmailInput', 
        'window.removeEmailInput'
    ]
    
    results = {}
    
    for func in email_functions:
        # Count occurrences
        count = content.count(func + ' =')
        results[func] = count
        
        if count == 0:
            print(f"❌ {func} not found!")
        elif count == 1:
            print(f"✅ {func} found once (correct)")
        else:
            print(f"⚠️  {func} found {count} times (may have duplicates)")
    
    # Check for function calls in HTML
    print("\n🔍 Checking for function calls in HTML...")
    
    # Look for onchange/onblur/onclick calls
    function_calls = [
        'onchange="updateGroupAdditionalEmails(this)"',
        'onblur="updateGroupAdditionalEmails(this)"',
        'onclick="addEmailInput(this)"',
        'onclick="removeEmailInput(this)"'
    ]
    
    for call in function_calls:
        count = content.count(call)
        if count > 0:
            print(f"✅ Found {count} instances of: {call}")
        else:
            print(f"❌ Not found: {call}")
    
    # Check if functions are defined before they're called
    print("\n🔍 Checking function definition order...")
    
    # Find line numbers of function definitions
    lines = content.split('\n')
    
    func_def_lines = {}
    func_call_lines = {}
    
    for i, line in enumerate(lines):
        for func in email_functions:
            if func + ' =' in line:
                func_def_lines[func] = i + 1
            if func.replace('window.', '') + '(' in line and ('onchange=' in line or 'onblur=' in line or 'onclick=' in line):
                func_call_lines[func] = i + 1
    
    print("Function definition lines:")
    for func, line_num in func_def_lines.items():
        print(f"  {func}: line {line_num}")
    
    print("Function call lines:")
    for func, line_num in func_call_lines.items():
        print(f"  {func}: line {line_num}")
    
    # Check if definitions come before calls
    all_good = True
    for func in email_functions:
        if func in func_def_lines and func in func_call_lines:
            if func_def_lines[func] > func_call_lines[func]:
                print(f"❌ {func} is defined AFTER it's called!")
                all_good = False
            else:
                print(f"✅ {func} is defined BEFORE it's called")
    
    return all_good

def test_tailwind_cdn():
    """Test for Tailwind CSS CDN usage."""
    
    html_file = Path("main/templates/main/shipment_list_clean.html")
    
    if not html_file.exists():
        print("❌ HTML file not found!")
        return False
    
    print("\n🔍 Checking for Tailwind CSS CDN usage...")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for CDN usage
    cdn_patterns = [
        'cdn.tailwindcss.com',
        'https://cdn.tailwindcss.com',
        'tailwindcss.com'
    ]
    
    found_cdn = False
    for pattern in cdn_patterns:
        if pattern in content:
            print(f"⚠️  Found Tailwind CDN usage: {pattern}")
            found_cdn = True
    
    if not found_cdn:
        print("✅ No Tailwind CDN usage found")
    else:
        print("❌ Tailwind CDN should not be used in production!")
        print("   Consider installing Tailwind CSS locally or using PostCSS plugin")
    
    return not found_cdn

def test_javascript_syntax():
    """Test for JavaScript syntax errors in the HTML file."""
    
    html_file = Path("main/templates/main/shipment_list_clean.html")
    
    if not html_file.exists():
        print("❌ HTML file not found!")
        return False
    
    print("\n🔍 Checking for JavaScript syntax issues...")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract JavaScript code
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)
    
    issues_found = 0
    
    for i, script in enumerate(scripts):
        # Check for common syntax issues
        if 'function(' in script and 'function (' in script:
            print(f"⚠️  Mixed function declaration styles in script {i+1}")
            issues_found += 1
        
        # Check for unclosed strings
        if script.count('"') % 2 != 0:
            print(f"⚠️  Unclosed string in script {i+1}")
            issues_found += 1
        
        if script.count("'") % 2 != 0:
            print(f"⚠️  Unclosed string in script {i+1}")
            issues_found += 1
    
    if issues_found == 0:
        print("✅ No obvious JavaScript syntax issues found")
    
    return issues_found == 0

def main():
    """Run all tests."""
    
    print("🧪 Testing Email Functions and HTML Issues")
    print("=" * 50)
    
    tests = [
        ("Email Functions", test_email_functions_in_html),
        ("Tailwind CDN", test_tailwind_cdn),
        ("JavaScript Syntax", test_javascript_syntax)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error in {test_name} test: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

