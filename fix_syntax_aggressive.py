#!/usr/bin/env python3
"""
Aggressive JavaScript syntax fixer - finds and removes extra closing braces/parentheses.
"""

import re
from pathlib import Path

def fix_javascript_syntax():
    """Find and fix JavaScript syntax errors by removing extra closing braces/parentheses."""
    
    template_path = Path("main/templates/main/shipment_list_clean.html")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 AGGRESSIVE SYNTAX FIXER")
    print("=" * 50)
    
    # Find all script sections
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)
    
    print(f"Found {len(scripts)} script sections")
    
    # Focus on Script Section 4 (index 3) which has the errors
    if len(scripts) >= 4:
        script_4 = scripts[3]
        print(f"\n🎯 FIXING SCRIPT SECTION 4")
        print(f"Original length: {len(script_4)} characters")
        
        # Count current braces and parentheses
        open_braces = script_4.count('{')
        close_braces = script_4.count('}')
        open_parens = script_4.count('(')
        close_parens = script_4.count(')')
        
        print(f"Before fix:")
        print(f"  Braces: {open_braces} open, {close_braces} close (diff: {close_braces - open_braces})")
        print(f"  Parentheses: {open_parens} open, {close_parens} close (diff: {close_parens - open_parens})")
        
        # Remove extra closing braces (2 extra)
        extra_braces = close_braces - open_braces
        if extra_braces > 0:
            print(f"\n🔧 Removing {extra_braces} extra closing braces...")
            
            # Find standalone closing braces and remove them
            lines = script_4.split('\n')
            removed_braces = 0
            
            for i, line in enumerate(lines):
                # Look for lines that are just whitespace + }
                if re.match(r'^\s*}\s*$', line) and removed_braces < extra_braces:
                    # Check if this brace is actually needed by looking at context
                    # Remove lines that are just standalone closing braces
                    if removed_braces < extra_braces:
                        print(f"  Removing extra brace at line {i+1}: '{line.strip()}'")
                        lines[i] = ''  # Remove the line
                        removed_braces += 1
            
            script_4 = '\n'.join(lines)
            print(f"  Removed {removed_braces} extra closing braces")
        
        # Remove extra closing parentheses (1 extra)
        extra_parens = close_parens - open_parens
        if extra_parens > 0:
            print(f"\n🔧 Removing {extra_parens} extra closing parentheses...")
            
            # Find and remove extra closing parentheses
            lines = script_4.split('\n')
            removed_parens = 0
            
            for i, line in enumerate(lines):
                # Look for lines with extra closing parentheses
                if ')' in line and removed_parens < extra_parens:
                    # Count parentheses in this line
                    line_open = line.count('(')
                    line_close = line.count(')')
                    
                    if line_close > line_open:
                        # This line has more closing than opening parentheses
                        excess = line_close - line_open
                        if removed_parens + excess <= extra_parens:
                            # Remove excess closing parentheses from this line
                            new_line = line
                            for _ in range(excess):
                                # Remove the last closing parenthesis
                                new_line = new_line.rsplit(')', 1)[0] + new_line.rsplit(')', 1)[1]
                            
                            print(f"  Removing {excess} extra parentheses from line {i+1}")
                            lines[i] = new_line
                            removed_parens += excess
            
            script_4 = '\n'.join(lines)
            print(f"  Removed {removed_parens} extra closing parentheses")
        
        # Reconstruct the content with the fixed script
        script_sections = re.split(script_pattern, content, flags=re.DOTALL)
        
        # Replace the 4th script section (index 6 in the split result)
        if len(script_sections) >= 7:
            script_sections[6] = script_4
            content = ''.join(script_sections)
        
        # Verify the fix
        new_scripts = re.findall(script_pattern, content, re.DOTALL)
        if len(new_scripts) >= 4:
            new_script_4 = new_scripts[3]
            new_open_braces = new_script_4.count('{')
            new_close_braces = new_script_4.count('}')
            new_open_parens = new_script_4.count('(')
            new_close_parens = new_script_4.count(')')
            
            print(f"\n✅ After fix:")
            print(f"  Braces: {new_open_braces} open, {new_close_braces} close (diff: {new_close_braces - new_open_braces})")
            print(f"  Parentheses: {new_open_parens} open, {new_close_parens} close (diff: {new_close_parens - new_open_parens})")
            
            if new_close_braces == new_open_braces and new_close_parens == new_open_parens:
                print("🎉 SYNTAX ERRORS FIXED!")
                
                # Write the fixed content back to the file
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("💾 Template file updated with fixes")
                return True
            else:
                print("❌ Still has syntax errors")
                return False
        else:
            print("❌ Could not reconstruct script sections")
            return False
    else:
        print("❌ Script section 4 not found")
        return False

if __name__ == "__main__":
    success = fix_javascript_syntax()
    
    if success:
        print("\n🚀 Running final test...")
        import subprocess
        result = subprocess.run(['python', 'test_km_functions.py'], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    else:
        print("\n❌ Fix failed - trying alternative approach...")
        
        # Alternative: Remove all standalone closing braces and parentheses
        print("🔧 ALTERNATIVE: Removing all standalone closing syntax...")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find script sections
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, content, re.DOTALL)
        
        if len(scripts) >= 4:
            script_4 = scripts[3]
            lines = script_4.split('\n')
            
            # Remove lines that are just standalone closing braces or parentheses
            fixed_lines = []
            removed_count = 0
            
            for line in lines:
                stripped = line.strip()
                # Remove lines that are just } or ) or }); or similar
                if re.match(r'^[}\s]*$', stripped) or re.match(r'^[)\s]*$', stripped):
                    print(f"  Removing standalone closing syntax: '{stripped}'")
                    removed_count += 1
                else:
                    fixed_lines.append(line)
            
            print(f"  Removed {removed_count} lines with standalone closing syntax")
            
            # Reconstruct
            script_sections = re.split(script_pattern, content, flags=re.DOTALL)
            if len(script_sections) >= 7:
                script_sections[6] = '\n'.join(fixed_lines)
                content = ''.join(script_sections)
                
                # Write back
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("💾 Template file updated with alternative fix")
                
                # Test again
                print("\n🚀 Running final test...")
                import subprocess
                result = subprocess.run(['python', 'test_km_functions.py'], capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print("Errors:", result.stderr)
