#!/usr/bin/env python3
"""
Simple test script to verify the JavaScript fixes work
"""

import os
import sys
from pathlib import Path

def test_javascript_fixes():
    """Test that JavaScript syntax errors have been fixed"""
    print("Testing JavaScript syntax fixes...")
    
    template_path = Path("main/templates/main/shipment_list_clean.html")
    
    if not template_path.exists():
        print("ERROR: Template file not found!")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Check that textConten;t typo is fixed
    if "textConten;t" in content:
        print("ERROR: JavaScript typo 'textConten;t' still exists!")
        return False
    else:
        print("PASS: JavaScript typo 'textConten;t' has been fixed")
    
    # Test 2: Check that semicolon inside object is fixed
    if "_force_refresh: true\n                ;};" in content:
        print("ERROR: JavaScript syntax error with semicolon inside object still exists!")
        return False
    else:
        print("PASS: JavaScript syntax error with semicolon inside object has been fixed")
    
    return True

def test_rfi_invoice_function():
    """Test that the new RFI/Invoice button function exists"""
    print("\nTesting RFI/Invoice button function...")
    
    template_path = Path("main/templates/main/shipment_list_clean.html")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Check that makeRFIInvoiceButtonsGreen function exists
    if "function makeRFIInvoiceButtonsGreen()" in content:
        print("PASS: makeRFIInvoiceButtonsGreen function exists")
    else:
        print("ERROR: makeRFIInvoiceButtonsGreen function not found!")
        return False
    
    # Test 2: Check that function is called on page load
    if "setTimeout(makeRFIInvoiceButtonsGreen, 2000);" in content:
        print("PASS: Function is called on page load")
    else:
        print("ERROR: Function is not called on page load!")
        return False
    
    # Test 3: Check that function makes buttons green
    if "rfiButton.style.backgroundColor = '#28a745';" in content:
        print("PASS: Function sets RFI button to green")
    else:
        print("ERROR: RFI button green color not found!")
        return False
    
    if "invoiceButton.style.backgroundColor = '#28a745';" in content:
        print("PASS: Function sets Invoice button to green")
    else:
        print("ERROR: Invoice button green color not found!")
        return False
    
    return True

def main():
    """Main function"""
    print("JavaScript Fix Verification Test")
    print("=" * 40)
    
    # Change to the correct directory if needed
    if not Path("main").exists():
        print("ERROR: Please run this script from the project root directory")
        sys.exit(1)
    
    print("Starting tests...\n")
    
    # Run tests
    test1_passed = test_javascript_fixes()
    test2_passed = test_rfi_invoice_function()
    
    print("\n" + "=" * 40)
    print("TEST RESULTS")
    print("=" * 40)
    
    if test1_passed and test2_passed:
        print("SUCCESS: All tests passed!")
        print("\nNext steps:")
        print("1. Start Django server: python manage.py runserver")
        print("2. Go to inspections page")
        print("3. Open browser console (F12)")
        print("4. Look for console messages about RFI/Invoice buttons")
        print("5. Check that buttons turn green when files exist")
        return True
    else:
        print("FAILED: Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)