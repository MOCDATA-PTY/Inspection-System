#!/usr/bin/env python3
"""
Fix the final syntax errors in the last lines of Script Section 4
"""

import re
import os

def fix_final_syntax_errors():
    template_path = 'main/templates/main/shipment_list_clean.html'
    
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        return
    
    print("Reading template file...")
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find Script Section 4
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)
    
    if len(scripts) < 4:
        print("Error: Could not find Script Section 4")
        return
    
    script_4 = scripts[3]
    print(f"Script Section 4 length: {len(script_4)} characters")
    
    # Find the problematic lines at the end
    lines = script_4.split('\n')
    print(f"\nLast 15 lines of Script Section 4:")
    for i, line in enumerate(lines[-15:], len(lines)-14):
        print(f"{i:4d}: {line}")
    
    # Fix the specific syntax errors
    original_script = script_4
    
    # Fix the malformed attribute access
    script_4 = re.sub(r"'data-inspection-id';\);", "'data-inspection-id');", script_4)
    
    # Fix the malformed property access
    script_4 = re.sub(r"dropdown\.valu;e;", "dropdown.value;", script_4)
    
    # Check if we made any changes
    if script_4 != original_script:
        print("\nFixed syntax errors:")
        print("- Fixed malformed attribute access: 'data-inspection-id';); -> 'data-inspection-id');")
        print("- Fixed malformed property access: dropdown.valu;e; -> dropdown.value;")
        
        # Replace the script in the content
        content = content.replace(original_script, script_4)
        
        # Create backup
        backup_path = f"{template_path}.backup_final_syntax_fix"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Backup created: {backup_path}")
        
        # Write fixed content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed template written to: {template_path}")
        
        # Verify the fix
        print("\nVerifying fix...")
        with open(template_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        new_scripts = re.findall(script_pattern, new_content, re.DOTALL)
        if len(new_scripts) >= 4:
            new_script_4 = new_scripts[3]
            new_open_braces = new_script_4.count('{')
            new_close_braces = new_script_4.count('}')
            new_open_parens = new_script_4.count('(')
            new_close_parens = new_script_4.count(')')
            
            print(f"Final braces: {new_open_braces} open, {new_close_braces} close, diff: {new_open_braces - new_close_braces}")
            print(f"Final parentheses: {new_open_parens} open, {new_close_parens} close, diff: {new_open_parens - new_close_parens}")
            
            # Show the last few lines to verify the fix
            new_lines = new_script_4.split('\n')
            print(f"\nLast 10 lines after fix:")
            for i, line in enumerate(new_lines[-10:], len(new_lines)-9):
                print(f"{i:4d}: {line}")
            
            if new_open_braces == new_close_braces and new_open_parens == new_close_parens:
                print("✅ Syntax fix successful!")
            else:
                print("❌ Syntax fix incomplete - still have unmatched braces/parentheses")
    else:
        print("No syntax errors found to fix")

if __name__ == "__main__":
    fix_final_syntax_errors()
