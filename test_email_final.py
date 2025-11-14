#!/usr/bin/env python3
"""
Comprehensive test script to verify email management functions are working correctly
in the inspection system before browser testing.
"""

import os
import re
import sys
from pathlib import Path

def test_email_functions_comprehensive():
    """Comprehensive test of email functions in HTML file."""
    
    html_file = Path("main/templates/main/shipment_list_clean.html")
    
    if not html_file.exists():
        print("❌ HTML file not found!")
        return False
    
    print("🔍 Comprehensive Email Functions Test")
    print("=" * 50)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Check for syntax errors
    print("\n📋 Test 1: JavaScript Syntax Check")
    syntax_ok = test_javascript_syntax(content)
    
    # Test 2: Check email function definitions
    print("\n📋 Test 2: Email Function Definitions")
    functions_ok = test_email_function_definitions(content)
    
    # Test 3: Check function call order
    print("\n📋 Test 3: Function Call Order")
    order_ok = test_function_call_order(content)
    
    # Test 4: Check for duplicates
    print("\n📋 Test 4: Duplicate Function Check")
    duplicates_ok = test_duplicate_functions(content)
    
    # Test 5: Check HTML event handlers
    print("\n📋 Test 5: HTML Event Handlers")
    handlers_ok = test_html_event_handlers(content)
    
    # Test 6: Check script structure
    print("\n📋 Test 6: Script Structure")
    structure_ok = test_script_structure(content)
    
    # Test 7: Check for common JavaScript errors
    print("\n📋 Test 7: Common JavaScript Errors")
    errors_ok = test_common_js_errors(content)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 50)
    
    tests = [
        ("JavaScript Syntax", syntax_ok),
        ("Email Function Definitions", functions_ok),
        ("Function Call Order", order_ok),
        ("Duplicate Functions", duplicates_ok),
        ("HTML Event Handlers", handlers_ok),
        ("Script Structure", structure_ok),
        ("Common JS Errors", errors_ok)
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
        print("⚠️  Some tests failed. Fix issues before testing in browser.")
        return False

def test_javascript_syntax(content):
    """Test for JavaScript syntax errors."""
    
    # Extract all script blocks
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)
    
    issues_found = 0
    
    for i, script in enumerate(scripts):
        # Check for common syntax issues
        if '};);' in script:
            print(f"❌ Syntax error in script {i+1}: Found '}};);' (should be '}};')")
            issues_found += 1
        
        # Check for unclosed strings
        if script.count('"') % 2 != 0:
            print(f"❌ Unclosed string in script {i+1}")
            issues_found += 1
        
        if script.count("'") % 2 != 0:
            print(f"❌ Unclosed string in script {i+1}")
            issues_found += 1
        
        # Check for unclosed template literals
        if script.count('`') % 2 != 0:
            print(f"❌ Unclosed template literal in script {i+1}")
            issues_found += 1
        
        # Check for missing semicolons after function declarations
        if re.search(r'function\s+\w+\s*\([^)]*\)\s*\{[^}]*\}', script) and not re.search(r'function\s+\w+\s*\([^)]*\)\s*\{[^}]*\};', script):
            # This is a complex check, let's be more specific
            pass
    
    if issues_found == 0:
        print("✅ No JavaScript syntax issues found")
        return True
    else:
        print(f"❌ Found {issues_found} syntax issues")
        return False

def test_email_function_definitions(content):
    """Test that email functions are properly defined."""
    
    email_functions = [
        'window.updateGroupAdditionalEmails',
        'window.addEmailInput', 
        'window.removeEmailInput'
    ]
    
    all_defined = True
    
    for func in email_functions:
        # Count occurrences
        count = content.count(func + ' =')
        
        if count == 0:
            print(f"❌ {func} not defined!")
            all_defined = False
        elif count == 1:
            print(f"✅ {func} defined once")
        else:
            print(f"⚠️  {func} defined {count} times (may have duplicates)")
    
    return all_defined

def test_function_call_order(content):
    """Test that functions are defined before they're called."""
    
    lines = content.split('\n')
    
    func_def_lines = {}
    func_call_lines = {}
    
    for i, line in enumerate(lines):
        # Find main function definitions (not fallback safety checks)
        if 'window.updateGroupAdditionalEmails =' in line and not ('if (typeof window.updateGroupAdditionalEmails === \'undefined\')' in lines[i-1] if i > 0 else False):
            func_def_lines['updateGroupAdditionalEmails'] = i + 1
        if 'window.addEmailInput =' in line and not ('if (typeof window.addEmailInput === \'undefined\')' in lines[i-1] if i > 0 else False):
            func_def_lines['addEmailInput'] = i + 1
        if 'window.removeEmailInput =' in line and not ('if (typeof window.removeEmailInput === \'undefined\')' in lines[i-1] if i > 0 else False):
            func_def_lines['removeEmailInput'] = i + 1
        
        # Find function calls in HTML
        if 'onchange="updateGroupAdditionalEmails(this)"' in line:
            func_call_lines['updateGroupAdditionalEmails'] = i + 1
        if 'onclick="addEmailInput(this)"' in line:
            func_call_lines['addEmailInput'] = i + 1
        if 'onclick="removeEmailInput(this)"' in line:
            func_call_lines['removeEmailInput'] = i + 1
    
    all_good = True
    
    for func in ['updateGroupAdditionalEmails', 'addEmailInput', 'removeEmailInput']:
        if func in func_def_lines and func in func_call_lines:
            if func_def_lines[func] > func_call_lines[func]:
                print(f"❌ {func} is defined AFTER it's called!")
                all_good = False
            else:
                print(f"✅ {func} is defined BEFORE it's called")
        elif func in func_def_lines:
            print(f"✅ {func} is defined (no HTML calls found)")
        else:
            print(f"❌ {func} is not defined!")
            all_good = False
    
    return all_good

def test_duplicate_functions(content):
    """Test for duplicate function definitions (excluding fallback safety checks)."""
    
    email_functions = [
        'window.updateGroupAdditionalEmails',
        'window.addEmailInput', 
        'window.removeEmailInput'
    ]
    
    no_duplicates = True
    
    for func in email_functions:
        # Count main definitions (not inside conditional checks)
        main_definitions = 0
        fallback_definitions = 0
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if func + ' =' in line:
                # Check if this is inside a conditional check
                if 'if (typeof ' + func + ' === \'undefined\')' in lines[i-1] if i > 0 else False:
                    fallback_definitions += 1
                else:
                    main_definitions += 1
        
        if main_definitions > 1:
            print(f"❌ {func} has {main_definitions} main definitions (duplicates found)")
            no_duplicates = False
        elif main_definitions == 1:
            print(f"✅ {func} has 1 main definition (+ {fallback_definitions} fallback safety checks)")
        else:
            print(f"❌ {func} has no main definition!")
            no_duplicates = False
    
    return no_duplicates

def test_html_event_handlers(content):
    """Test that HTML event handlers are properly set up."""
    
    handlers = [
        'onchange="updateGroupAdditionalEmails(this)"',
        'onblur="updateGroupAdditionalEmails(this)"',
        'onclick="addEmailInput(this)"',
        'onclick="removeEmailInput(this)"'
    ]
    
    all_found = True
    
    for handler in handlers:
        count = content.count(handler)
        if count > 0:
            print(f"✅ Found {count} instances of: {handler}")
        else:
            print(f"❌ Not found: {handler}")
            all_found = False
    
    return all_found

def test_script_structure(content):
    """Test the overall script structure."""
    
    # Check for proper script tags
    script_open = content.count('<script>')
    script_close = content.count('</script>')
    
    if script_open == script_close:
        print(f"✅ Script tags balanced: {script_open} open, {script_close} close")
        return True
    else:
        print(f"❌ Script tags unbalanced: {script_open} open, {script_close} close")
        return False

def test_common_js_errors(content):
    """Test for common JavaScript errors."""
    
    errors_found = 0
    
    # Check for common error patterns
    error_patterns = [
        (r'};\);', "Syntax error: '};);' should be '};'"),
        (r'function\s*\(\s*\)\s*\{[^}]*\}\s*\(\s*\)', "IIFE syntax error"),
        (r'window\.\w+\s*=\s*function.*?\{[^}]*\}\s*\(\s*\)', "Function assignment error"),
    ]
    
    for pattern, description in error_patterns:
        if re.search(pattern, content, re.DOTALL):
            print(f"❌ {description}")
            errors_found += 1
    
    if errors_found == 0:
        print("✅ No common JavaScript errors found")
        return True
    else:
        print(f"❌ Found {errors_found} common JavaScript errors")
        return False

def main():
    """Run comprehensive email functions test."""
    
    print("🧪 Comprehensive Email Functions Test")
    print("Testing before browser verification...")
    
    try:
        result = test_email_functions_comprehensive()
        if result:
            print("\n🎉 READY FOR BROWSER TESTING!")
            print("All email functions should work correctly now.")
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
