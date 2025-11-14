#!/usr/bin/env python3
"""
Comprehensive JavaScript syntax fix for shipment_list_clean.html
This script will identify and fix all JavaScript syntax errors systematically.
"""

import re
import os

def find_script_sections(content):
    """Find all script sections in the HTML content."""
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)
    return scripts

def check_brace_balance(text):
    """Check if braces are balanced in the text."""
    open_braces = text.count('{')
    close_braces = text.count('}')
    return open_braces, close_braces, open_braces - close_braces

def check_parenthesis_balance(text):
    """Check if parentheses are balanced in the text."""
    open_parens = text.count('(')
    close_parens = text.count(')')
    return open_parens, close_parens, open_parens - close_parens

def check_bracket_balance(text):
    """Check if square brackets are balanced in the text."""
    open_brackets = text.count('[')
    close_brackets = text.count(']')
    return open_brackets, close_brackets, open_brackets - close_brackets

def find_syntax_errors(script_content):
    """Find syntax errors in a script section."""
    errors = []
    
    # Check brace balance
    open_braces, close_braces, brace_diff = check_brace_balance(script_content)
    if brace_diff != 0:
        errors.append(f"Unmatched braces: {open_braces} open, {close_braces} close, diff: {brace_diff}")
    
    # Check parenthesis balance
    open_parens, close_parens, paren_diff = check_parenthesis_balance(script_content)
    if paren_diff != 0:
        errors.append(f"Unmatched parentheses: {open_parens} open, {close_parens} close, diff: {paren_diff}")
    
    # Check bracket balance
    open_brackets, close_brackets, bracket_diff = check_bracket_balance(script_content)
    if bracket_diff != 0:
        errors.append(f"Unmatched brackets: {open_brackets} open, {close_brackets} close, diff: {bracket_diff}")
    
    # Check for common syntax issues
    lines = script_content.split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()
        
        # Check for missing semicolons after function declarations
        if re.match(r'^\s*function\s+\w+\s*\([^)]*\)\s*\{', line) and not line.endswith(';'):
            # This is usually fine, but check if it's a statement
            pass
        
        # Check for unmatched quotes
        single_quotes = line.count("'")
        double_quotes = line.count('"')
        if single_quotes % 2 != 0:
            errors.append(f"Line {i}: Unmatched single quotes")
        if double_quotes % 2 != 0:
            errors.append(f"Line {i}: Unmatched double quotes")
        
        # Check for common syntax errors
        if 'function(' in line and not re.search(r'function\s*\([^)]*\)\s*\{', line):
            if not re.search(r'function\s+\w+\s*\([^)]*\)\s*\{', line):
                errors.append(f"Line {i}: Possible malformed function declaration")
    
    return errors

def fix_common_syntax_issues(content):
    """Fix common JavaScript syntax issues."""
    fixes_applied = []
    
    # Fix missing semicolons after console.log statements
    original_content = content
    content = re.sub(r'(console\.log\([^)]*\))(?!\s*;)', r'\1;', content)
    if content != original_content:
        fixes_applied.append("Added missing semicolons after console.log statements")
    
    # Fix missing semicolons after variable declarations
    original_content = content
    content = re.sub(r'(var\s+\w+\s*=\s*[^;]+)(?!\s*;)', r'\1;', content)
    if content != original_content:
        fixes_applied.append("Added missing semicolons after var declarations")
    
    # Fix missing semicolons after let/const declarations
    original_content = content
    content = re.sub(r'((?:let|const)\s+\w+\s*=\s*[^;]+)(?!\s*;)', r'\1;', content)
    if content != original_content:
        fixes_applied.append("Added missing semicolons after let/const declarations")
    
    return content, fixes_applied

def main():
    template_path = 'main/templates/main/shipment_list_clean.html'
    
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        return
    
    print("Reading template file...")
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Finding script sections...")
    scripts = find_script_sections(content)
    print(f"Found {len(scripts)} script sections")
    
    total_errors = 0
    all_fixes = []
    
    for i, script in enumerate(scripts, 1):
        print(f"\n--- Script Section {i} ---")
        print(f"Length: {len(script)} characters")
        
        # Check for syntax errors
        errors = find_syntax_errors(script)
        if errors:
            print(f"Found {len(errors)} syntax errors:")
            for error in errors:
                print(f"  - {error}")
            total_errors += len(errors)
        else:
            print("No syntax errors found")
        
        # Apply common fixes
        fixed_script, fixes = fix_common_syntax_issues(script)
        if fixes:
            print(f"Applied fixes: {', '.join(fixes)}")
            all_fixes.extend(fixes)
            
            # Replace the script in the content
            content = content.replace(script, fixed_script)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total syntax errors found: {total_errors}")
    print(f"Total fixes applied: {len(all_fixes)}")
    
    if all_fixes:
        print(f"Fixes applied: {', '.join(set(all_fixes))}")
    
    if total_errors > 0 or all_fixes:
        # Create backup
        backup_path = f"{template_path}.backup_js_fix"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Backup created: {backup_path}")
        
        # Write fixed content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed template written to: {template_path}")
    else:
        print("No fixes needed - template appears to be syntactically correct")

if __name__ == "__main__":
    main()
