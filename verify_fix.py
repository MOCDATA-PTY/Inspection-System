#!/usr/bin/env python3
"""Verify the JavaScript syntax fix."""

import re
from pathlib import Path

def verify_fix():
    template_path = Path("main/templates/main/shipment_list_clean.html")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all script sections
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    
    print(f"Found {len(scripts)} script sections")
    
    for i, script in enumerate(scripts):
        if len(script) > 1000:  # Only check large scripts
            open_braces = script.count('{')
            close_braces = script.count('}')
            open_parens = script.count('(')
            close_parens = script.count(')')
            
            print(f"Script {i+1}: {len(script)} chars")
            print(f"  Braces: {open_braces} open, {close_braces} close (diff: {close_braces - open_braces})")
            print(f"  Parentheses: {open_parens} open, {close_parens} close (diff: {close_parens - open_parens})")
            
            if close_braces == open_braces and close_parens == open_parens:
                print("  ✅ SYNTAX OK")
            else:
                print("  ❌ SYNTAX ERRORS")

if __name__ == "__main__":
    verify_fix()
