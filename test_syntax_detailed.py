#!/usr/bin/env python3
"""
Detailed syntax checker for JavaScript in HTML template.
"""

import re
from pathlib import Path

def check_script_syntax():
    """Check JavaScript syntax in each script section."""
    
    template_path = Path("main/templates/main/shipment_list_clean.html")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all script sections
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)
    
    print(f"Found {len(scripts)} script sections")
    
    for i, script in enumerate(scripts):
        print(f"\n--- Script Section {i+1} ---")
        print(f"Length: {len(script)} characters")
        
        # Count braces
        open_braces = script.count('{')
        close_braces = script.count('}')
        print(f"Braces: {open_braces} open, {close_braces} close")
        
        # Count parentheses
        open_parens = script.count('(')
        close_parens = script.count(')')
        print(f"Parentheses: {open_parens} open, {close_parens} close")
        
        # Count brackets
        open_brackets = script.count('[')
        close_brackets = script.count(']')
        print(f"Brackets: {open_brackets} open, {close_brackets} close")
        
        # Check for incomplete function definitions
        function_defs = re.findall(r'function\s+\w+\s*\([^)]*\)\s*\{', script)
        print(f"Function definitions found: {len(function_defs)}")
        
        # Check for incomplete arrow functions
        arrow_functions = re.findall(r'\w+\s*=>\s*\{', script)
        print(f"Arrow functions found: {len(arrow_functions)}")
        
        # Check for incomplete async functions
        async_functions = re.findall(r'async\s+function\s+\w+\s*\([^)]*\)\s*\{', script)
        print(f"Async functions found: {len(async_functions)}")
        
        # Show first few lines of script
        lines = script.strip().split('\n')[:5]
        print("First few lines:")
        for j, line in enumerate(lines):
            print(f"  {j+1}: {line.strip()}")
        
        # Show last few lines of script
        if len(lines) > 5:
            last_lines = script.strip().split('\n')[-5:]
            print("Last few lines:")
            for j, line in enumerate(last_lines):
                print(f"  {len(script.strip().split('\n'))-5+j+1}: {line.strip()}")
        
        # Check for specific issues
        issues = []
        if open_braces != close_braces:
            issues.append(f"Unmatched braces: {open_braces} open, {close_braces} close")
        if open_parens != close_parens:
            issues.append(f"Unmatched parentheses: {open_parens} open, {close_parens} close")
        if open_brackets != close_brackets:
            issues.append(f"Unmatched brackets: {open_brackets} open, {close_brackets} close")
        
        if issues:
            print("❌ Issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ No syntax issues found")

if __name__ == "__main__":
    check_script_syntax()
