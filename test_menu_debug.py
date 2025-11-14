#!/usr/bin/env python3
"""
Menu Button Debug Test Script
This script analyzes the shipment_list_clean.html file to identify potential issues with the mobile menu functionality.
"""

import re
import os
from datetime import datetime

def analyze_html_file(file_path):
    """Analyze the HTML file for menu-related issues."""
    print("🔍 MENU BUTTON DEBUG ANALYSIS")
    print("=" * 50)
    print(f"📁 File: {file_path}")
    print(f"⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ File not found!")
        return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Check file size
    file_size = len(content)
    print(f"📊 File size: {file_size:,} characters")
    print()
    
    # 1. Check for mobile menu button HTML
    print("1️⃣ CHECKING MOBILE MENU BUTTON HTML")
    print("-" * 40)
    
    mobile_btn_pattern = r'<button[^>]*id="mobile-menu-btn"[^>]*>'
    mobile_btn_matches = re.findall(mobile_btn_pattern, content, re.IGNORECASE)
    
    if mobile_btn_matches:
        print("✅ Mobile menu button found:")
        for i, match in enumerate(mobile_btn_matches, 1):
            print(f"   {i}. {match}")
    else:
        print("❌ Mobile menu button NOT found!")
    
    print()
    
    # 2. Check for sidebar HTML
    print("2️⃣ CHECKING SIDEBAR HTML")
    print("-" * 40)
    
    sidebar_pattern = r'<div[^>]*id="sidebar"[^>]*>'
    sidebar_matches = re.findall(sidebar_pattern, content, re.IGNORECASE)
    
    if sidebar_matches:
        print("✅ Sidebar found:")
        for i, match in enumerate(sidebar_matches, 1):
            print(f"   {i}. {match}")
    else:
        print("❌ Sidebar NOT found!")
    
    print()
    
    # 3. Check for sidebar overlay HTML
    print("3️⃣ CHECKING SIDEBAR OVERLAY HTML")
    print("-" * 40)
    
    overlay_pattern = r'<div[^>]*id="sidebar-overlay"[^>]*>'
    overlay_matches = re.findall(overlay_pattern, content, re.IGNORECASE)
    
    if overlay_matches:
        print("✅ Sidebar overlay found:")
        for i, match in enumerate(overlay_matches, 1):
            print(f"   {i}. {match}")
    else:
        print("❌ Sidebar overlay NOT found!")
    
    print()
    
    # 4. Check for CSS classes
    print("4️⃣ CHECKING CSS CLASSES")
    print("-" * 40)
    
    # Check for .show class
    show_class_pattern = r'\.show\s*\{[^}]*\}'
    show_class_matches = re.findall(show_class_pattern, content, re.IGNORECASE | re.DOTALL)
    
    if show_class_matches:
        print("✅ .show class found:")
        for i, match in enumerate(show_class_matches, 1):
            print(f"   {i}. {match[:100]}...")
    else:
        print("❌ .show class NOT found!")
    
    # Check for mobile-menu-btn CSS
    mobile_btn_css_pattern = r'\.mobile-menu-btn\s*\{[^}]*\}'
    mobile_btn_css_matches = re.findall(mobile_btn_css_pattern, content, re.IGNORECASE | re.DOTALL)
    
    if mobile_btn_css_matches:
        print("✅ .mobile-menu-btn CSS found:")
        for i, match in enumerate(mobile_btn_css_matches, 1):
            print(f"   {i}. {match[:100]}...")
    else:
        print("❌ .mobile-menu-btn CSS NOT found!")
    
    print()
    
    # 5. Check for JavaScript functions
    print("5️⃣ CHECKING JAVASCRIPT FUNCTIONS")
    print("-" * 40)
    
    # Check for toggleSidebar function
    toggle_function_pattern = r'function\s+toggleSidebar\s*\([^)]*\)\s*\{'
    toggle_function_matches = re.findall(toggle_function_pattern, content, re.IGNORECASE)
    
    if toggle_function_matches:
        print("✅ toggleSidebar function found:")
        for i, match in enumerate(toggle_function_matches, 1):
            print(f"   {i}. {match}")
    else:
        print("❌ toggleSidebar function NOT found!")
    
    # Check for event listeners
    event_listener_pattern = r'addEventListener\s*\(\s*[\'"]click[\'"]\s*,\s*toggleSidebar\s*\)'
    event_listener_matches = re.findall(event_listener_pattern, content, re.IGNORECASE)
    
    if event_listener_matches:
        print("✅ Click event listeners found:")
        for i, match in enumerate(event_listener_matches, 1):
            print(f"   {i}. {match}")
    else:
        print("❌ Click event listeners NOT found!")
    
    print()
    
    # 6. Check for JavaScript errors
    print("6️⃣ CHECKING FOR JAVASCRIPT SYNTAX ISSUES")
    print("-" * 40)
    
    # Check for common syntax errors
    syntax_issues = []
    
    # Check for missing semicolons before function declarations
    missing_semicolon_pattern = r'}\s*function\s+'
    if re.search(missing_semicolon_pattern, content):
        syntax_issues.append("Missing semicolon before function declaration")
    
    # Check for malformed setTimeout calls
    malformed_settimeout_pattern = r';\s*,\s*\d+\s*\)\s*;'
    if re.search(malformed_settimeout_pattern, content):
        syntax_issues.append("Malformed setTimeout call")
    
    # Check for unclosed strings
    unclosed_string_pattern = r'console\.log\([^)]*$'
    if re.search(unclosed_string_pattern, content, re.MULTILINE):
        syntax_issues.append("Unclosed console.log string")
    
    if syntax_issues:
        print("❌ Potential syntax issues found:")
        for i, issue in enumerate(syntax_issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("✅ No obvious syntax issues found")
    
    print()
    
    # 7. Check for console.log statements
    print("7️⃣ CHECKING DEBUG CONSOLE LOGS")
    print("-" * 40)
    
    console_log_pattern = r'console\.log\([^)]*🍔[^)]*\)'
    console_log_matches = re.findall(console_log_pattern, content)
    
    if console_log_matches:
        print(f"✅ Found {len(console_log_matches)} menu debug console.log statements:")
        for i, match in enumerate(console_log_matches[:5], 1):  # Show first 5
            print(f"   {i}. {match[:80]}...")
        if len(console_log_matches) > 5:
            print(f"   ... and {len(console_log_matches) - 5} more")
    else:
        print("❌ No menu debug console.log statements found!")
    
    print()
    
    # 8. Summary and recommendations
    print("8️⃣ SUMMARY AND RECOMMENDATIONS")
    print("-" * 40)
    
    issues_found = []
    
    if not mobile_btn_matches:
        issues_found.append("Mobile menu button HTML missing")
    if not sidebar_matches:
        issues_found.append("Sidebar HTML missing")
    if not overlay_matches:
        issues_found.append("Sidebar overlay HTML missing")
    if not show_class_matches:
        issues_found.append(".show CSS class missing")
    if not toggle_function_matches:
        issues_found.append("toggleSidebar function missing")
    if not event_listener_matches:
        issues_found.append("Click event listeners missing")
    if not console_log_matches:
        issues_found.append("Debug console logs missing")
    
    if issues_found:
        print("❌ Issues found:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
    else:
        print("✅ All menu components appear to be present!")
    
    print()
    print("🔧 RECOMMENDATIONS:")
    print("1. Hard refresh the browser (Ctrl+Shift+R)")
    print("2. Check browser console for JavaScript errors")
    print("3. Verify the page is loading the updated HTML file")
    print("4. Test on mobile device or resize browser window to <1024px")
    print("5. Check if any external JavaScript files are causing conflicts")
    
    print()
    print("=" * 50)
    print("🏁 Analysis complete!")

def main():
    """Main function to run the analysis."""
    file_path = "main/templates/main/shipment_list_clean.html"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        print("Please run this script from the project root directory.")
        return
    
    analyze_html_file(file_path)

if __name__ == "__main__":
    main()
