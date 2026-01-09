#!/usr/bin/env python3
"""
Fix the remaining JavaScript syntax errors in Script Section 4
Specifically targeting the 2 extra closing braces and 2 extra closing parentheses
"""

import re
import os

def fix_syntax_errors():
    template_path = 'main/templates/main/shipment_list_clean.html'
    
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        return
    
    print("Reading template file...")
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find Script Section 4 (the large one with the KM functions)
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)
    
    if len(scripts) < 4:
        print("Error: Could not find Script Section 4")
        return
    
    script_4 = scripts[3]  # Script Section 4 (0-indexed)
    print(f"Script Section 4 length: {len(script_4)} characters")
    
    # Count current braces and parentheses
    open_braces = script_4.count('{')
    close_braces = script_4.count('}')
    open_parens = script_4.count('(')
    close_parens = script_4.count(')')
    
    print(f"Current braces: {open_braces} open, {close_braces} close, diff: {open_braces - close_braces}")
    print(f"Current parentheses: {open_parens} open, {close_parens} close, diff: {open_parens - close_parens}")
    
    # We need to remove 2 extra closing braces and 2 extra closing parentheses
    # Let's find the end of the script and remove the extra characters
    
    # Find the last few lines to see what we're dealing with
    lines = script_4.split('\n')
    print(f"\nLast 10 lines of Script Section 4:")
    for i, line in enumerate(lines[-10:], len(lines)-9):
        print(f"{i:4d}: {line}")
    
    # Look for the end of the script section
    # The script should end with proper closing of functions
    # Let's find where the main functions end and remove extra characters
    
    # Find the last occurrence of proper function closing
    # Look for patterns like: }); or });\n or similar
    
    # Let's be more systematic - find the last proper closing
    # and remove any extra characters after it
    
    # Find the last meaningful line (not just whitespace or extra braces)
    last_meaningful_line = -1
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if line and not line in ['}', ');', '});']:
            last_meaningful_line = i
            break
    
    print(f"\nLast meaningful line: {last_meaningful_line + 1}")
    if last_meaningful_line >= 0:
        print(f"Content: {lines[last_meaningful_line]}")
    
    # Now let's find where the script should actually end
    # Look for the end of the main function or the last proper statement
    
    # Find the last proper closing brace that makes sense
    # We'll look for patterns that suggest the end of a function or block
    
    # Let's try a different approach - find the last occurrence of certain patterns
    # and remove everything after that
    
    # Look for the end of the main script logic
    # Find the last occurrence of a proper function ending
    
    # Let's find the last occurrence of certain key patterns
    patterns_to_find_end = [
        r'}\s*;\s*$',  # Function ending with };
        r'}\s*\)\s*;\s*$',  # Function ending with });
        r'}\s*$',  # Just closing brace
    ]
    
    end_position = -1
    for pattern in patterns_to_find_end:
        matches = list(re.finditer(pattern, script_4, re.MULTILINE))
        if matches:
            end_position = max(end_position, matches[-1].end())
    
    if end_position > 0:
        print(f"\nFound potential end position at character {end_position}")
        # Show what comes after this position
        after_end = script_4[end_position:end_position+200]
        print(f"Content after end position: {repr(after_end)}")
        
        # Remove everything after the end position
        script_4_fixed = script_4[:end_position]
        
        # Now add proper closing if needed
        # Check if we need to add any closing characters
        open_braces_fixed = script_4_fixed.count('{')
        close_braces_fixed = script_4_fixed.count('}')
        open_parens_fixed = script_4_fixed.count('(')
        close_parens_fixed = script_4_fixed.count(')')
        
        print(f"\nAfter fixing:")
        print(f"Braces: {open_braces_fixed} open, {close_braces_fixed} close, diff: {open_braces_fixed - close_braces_fixed}")
        print(f"Parentheses: {open_parens_fixed} open, {close_parens_fixed} close, diff: {open_parens_fixed - close_parens_fixed}")
        
        # If we still have unmatched braces/parentheses, add the missing ones
        if open_braces_fixed > close_braces_fixed:
            missing_braces = open_braces_fixed - close_braces_fixed
            print(f"Adding {missing_braces} missing closing braces")
            script_4_fixed += '}' * missing_braces
        
        if open_parens_fixed > close_parens_fixed:
            missing_parens = open_parens_fixed - close_parens_fixed
            print(f"Adding {missing_parens} missing closing parentheses")
            script_4_fixed += ')' * missing_parens
        
        # Replace the script in the content
        content = content.replace(script_4, script_4_fixed)
        
        # Create backup
        backup_path = f"{template_path}.backup_syntax_fix"
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
            
            if new_open_braces == new_close_braces and new_open_parens == new_close_parens:
                print("✅ Syntax fix successful!")
            else:
                print("❌ Syntax fix incomplete")
    else:
        print("Could not find proper end position")

if __name__ == "__main__":
    fix_syntax_errors()
