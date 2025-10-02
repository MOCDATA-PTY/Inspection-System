#!/usr/bin/env python3
"""
Find and remove the extra closing braces and parentheses at the end of Script Section 4
"""

import re
import os

def find_and_remove_extra_characters():
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
    
    # Find the end of the script content
    # Look for the last meaningful content
    lines = script_4.split('\n')
    
    # Find the last non-empty line
    last_non_empty = -1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():
            last_non_empty = i
            break
    
    print(f"Last non-empty line: {last_non_empty + 1}")
    print(f"Content: {lines[last_non_empty]}")
    
    # Look at the very end of the script
    print(f"\nLast 20 characters of script: {repr(script_4[-20:])}")
    
    # Find where the script should actually end
    # Look for the last proper function or statement ending
    
    # Find the last occurrence of proper closing patterns
    # The script should end with proper function closures
    
    # Let's find the last meaningful function or block
    # Look for patterns that suggest the end of the main script logic
    
    # Find the last occurrence of certain patterns that indicate proper ending
    end_patterns = [
        r'}\s*;\s*$',  # Function ending with };
        r'}\s*\)\s*;\s*$',  # Function ending with });
        r'}\s*$',  # Just closing brace
    ]
    
    # Find the last proper ending
    last_end_pos = -1
    for pattern in end_patterns:
        matches = list(re.finditer(pattern, script_4, re.MULTILINE))
        if matches:
            pos = matches[-1].end()
            if pos > last_end_pos:
                last_end_pos = pos
    
    if last_end_pos > 0:
        print(f"\nFound last proper ending at position {last_end_pos}")
        
        # Show what comes after this position
        after_end = script_4[last_end_pos:]
        print(f"Content after last proper ending: {repr(after_end)}")
        
        # Count braces and parentheses in the content after the proper ending
        extra_braces = after_end.count('}')
        extra_parens = after_end.count(')')
        
        print(f"Extra braces after proper ending: {extra_braces}")
        print(f"Extra parentheses after proper ending: {extra_parens}")
        
        # If we have exactly 2 extra braces and 2 extra parentheses, remove them
        if extra_braces == 2 and extra_parens == 2:
            print("Found exactly 2 extra braces and 2 extra parentheses - removing them")
            
            # Remove everything after the proper ending
            script_4_fixed = script_4[:last_end_pos]
            
            # Replace the script in the content
            content = content.replace(script_4, script_4_fixed)
            
            # Create backup
            backup_path = f"{template_path}.backup_remove_extra"
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
            print(f"Expected 2 extra braces and 2 extra parentheses, but found {extra_braces} braces and {extra_parens} parentheses")
    else:
        print("Could not find proper ending position")

if __name__ == "__main__":
    find_and_remove_extra_characters()
