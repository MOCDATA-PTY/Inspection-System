#!/usr/bin/env python3
"""
Direct JavaScript syntax fixer - removes extra closing braces/parentheses.
"""

import re
from pathlib import Path

def fix_syntax_direct():
    """Directly fix the JavaScript syntax errors."""
    
    template_path = Path("main/templates/main/shipment_list_clean.html")
    
    print("🔧 DIRECT SYNTAX FIXER")
    print("=" * 50)
    
    # Read the file
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic script section (the large one)
    script_pattern = r'<script[^>]*>(.*?)</script>'
    match = re.search(script_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ No script section found")
        return False
    
    # Find the largest script section (Script Section 4)
    all_scripts = re.findall(script_pattern, content, re.DOTALL)
    largest_script = max(all_scripts, key=len)
    
    print(f"Found largest script section: {len(largest_script)} characters")
    
    # Count braces and parentheses
    open_braces = largest_script.count('{')
    close_braces = largest_script.count('}')
    open_parens = largest_script.count('(')
    close_parens = largest_script.count(')')
    
    print(f"Before fix:")
    print(f"  Braces: {open_braces} open, {close_braces} close (diff: {close_braces - open_braces})")
    print(f"  Parentheses: {open_parens} open, {close_parens} close (diff: {close_parens - open_parens})")
    
    # Fix the script
    fixed_script = largest_script
    
    # Remove extra closing braces
    extra_braces = close_braces - open_braces
    if extra_braces > 0:
        print(f"\n🔧 Removing {extra_braces} extra closing braces...")
        
        # Find and remove standalone closing braces
        lines = fixed_script.split('\n')
        removed = 0
        
        for i, line in enumerate(lines):
            if re.match(r'^\s*}\s*$', line) and removed < extra_braces:
                print(f"  Removing extra brace at line {i+1}: '{line.strip()}'")
                lines[i] = ''
                removed += 1
        
        fixed_script = '\n'.join(lines)
        print(f"  Removed {removed} extra closing braces")
    
    # Remove extra closing parentheses
    extra_parens = close_parens - open_parens
    if extra_parens > 0:
        print(f"\n🔧 Removing {extra_parens} extra closing parentheses...")
        
        # Find and remove extra closing parentheses
        lines = fixed_script.split('\n')
        removed = 0
        
        for i, line in enumerate(lines):
            if ')' in line and removed < extra_parens:
                # Count parentheses in this line
                line_open = line.count('(')
                line_close = line.count(')')
                
                if line_close > line_open:
                    excess = min(line_close - line_open, extra_parens - removed)
                    if excess > 0:
                        # Remove excess closing parentheses
                        new_line = line
                        for _ in range(excess):
                            # Remove the last closing parenthesis
                            last_paren = new_line.rfind(')')
                            if last_paren != -1:
                                new_line = new_line[:last_paren] + new_line[last_paren+1:]
                        
                        print(f"  Removing {excess} extra parentheses from line {i+1}")
                        lines[i] = new_line
                        removed += excess
        
        fixed_script = '\n'.join(lines)
        print(f"  Removed {removed} extra closing parentheses")
    
    # Replace the script in the content
    content = content.replace(largest_script, fixed_script)
    
    # Verify the fix
    new_scripts = re.findall(script_pattern, content, re.DOTALL)
    new_largest = max(new_scripts, key=len)
    
    new_open_braces = new_largest.count('{')
    new_close_braces = new_largest.count('}')
    new_open_parens = new_largest.count('(')
    new_close_parens = new_largest.count(')')
    
    print(f"\n✅ After fix:")
    print(f"  Braces: {new_open_braces} open, {new_close_braces} close (diff: {new_close_braces - new_open_braces})")
    print(f"  Parentheses: {new_open_parens} open, {new_close_parens} close (diff: {new_close_parens - new_open_parens})")
    
    if new_close_braces == new_open_braces and new_close_parens == new_open_parens:
        print("🎉 SYNTAX ERRORS FIXED!")
        
        # Write the fixed content back
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("💾 Template file updated with fixes")
        return True
    else:
        print("❌ Still has syntax errors")
        return False

if __name__ == "__main__":
    success = fix_syntax_direct()
    
    if success:
        print("\n🚀 Running final test...")
        import subprocess
        result = subprocess.run(['python', 'test_km_functions.py'], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    else:
        print("\n❌ Fix failed")
