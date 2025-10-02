#!/usr/bin/env python3
"""
Find remaining JavaScript syntax errors in the rendered page
"""

import requests
from bs4 import BeautifulSoup
import re

def find_remaining_errors():
    """Find remaining JavaScript syntax errors"""
    print("🔍 Finding remaining JavaScript syntax errors...")
    
    session = requests.Session()
    
    try:
        # Login as developer
        login_page = session.get('http://127.0.0.1:8000/login/')
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        
        login_data = {
            'username': 'developer',
            'password': 'Dev2025!',
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post('http://127.0.0.1:8000/login/', data=login_data)
        
        # Get inspections page
        response = session.get('http://127.0.0.1:8000/inspections/')
        
        if response.status_code != 200:
            print(f"❌ Failed to get page: {response.status_code}")
            return False
            
        # Save the actual rendered HTML for debugging
        with open('current_rendered_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Extract JavaScript from rendered page
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        
        rendered_js = ""
        for i, script in enumerate(scripts):
            if script.string:
                rendered_js += f"\n// === SCRIPT BLOCK {i+1} ===\n"
                rendered_js += script.string
                rendered_js += f"\n// === END SCRIPT BLOCK {i+1} ===\n"
        
        # Save rendered JavaScript for analysis
        with open('current_rendered_js.js', 'w', encoding='utf-8') as f:
            f.write(rendered_js)
        
        print(f"💾 Saved current rendered page and JS for analysis")
        
        # Analyze the JavaScript line by line for syntax issues
        lines = rendered_js.split('\n')
        
        print(f"\n📊 JAVASCRIPT ANALYSIS:")
        print("="*60)
        print(f"Total lines: {len(lines)}")
        
        # Check balance
        brace_count = rendered_js.count('{') - rendered_js.count('}')
        paren_count = rendered_js.count('(') - rendered_js.count(')')
        bracket_count = rendered_js.count('[') - rendered_js.count(']')
        
        print(f"Brace balance: {brace_count}")
        print(f"Parentheses balance: {paren_count}")  
        print(f"Bracket balance: {bracket_count}")
        
        # Look for specific issues around line 17092 and 19747 area
        # Since these are very high line numbers, let's look for patterns
        
        issues_found = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip empty lines and comments
            if not line_stripped or line_stripped.startswith('//'):
                continue
                
            # Look for problematic patterns
            if line_stripped == '}' and i < len(lines):
                # Check what comes after a closing brace
                next_line = lines[i].strip() if i < len(lines) else ""
                if next_line and not next_line.startswith('//') and not next_line.startswith('else') and not next_line.startswith('catch') and not next_line.startswith('finally') and not next_line.startswith('}') and not next_line.endswith(';'):
                    if not next_line.startswith('function') and not next_line.startswith('var') and not next_line.startswith('const') and not next_line.startswith('let'):
                        issues_found.append(f"Line {i}: Possible missing semicolon after brace: '{line_stripped}' followed by '{next_line}'")
            
            # Look for unmatched quotes in non-comment lines
            if line_stripped.count("'") % 2 != 0:
                issues_found.append(f"Line {i}: Unmatched single quotes: {line_stripped}")
            
            if line_stripped.count('"') % 2 != 0:
                issues_found.append(f"Line {i}: Unmatched double quotes: {line_stripped}")
            
            # Look for specific problem patterns
            if 'html +=' in line_stripped and not line_stripped.endswith(';'):
                issues_found.append(f"Line {i}: Missing semicolon after html assignment: {line_stripped}")
                
            # Look for problematic template literal mixing
            if '`' in line_stripped and ("'" in line_stripped or '"' in line_stripped):
                quote_issues = []
                if line_stripped.count("'") % 2 != 0:
                    quote_issues.append("unmatched single quotes")
                if line_stripped.count('"') % 2 != 0:
                    quote_issues.append("unmatched double quotes")
                if quote_issues:
                    issues_found.append(f"Line {i}: Template literal with {', '.join(quote_issues)}: {line_stripped}")
        
        # Show first 20 issues
        if issues_found:
            print(f"\n❌ SYNTAX ISSUES FOUND ({len(issues_found)} total):")
            for issue in issues_found[:20]:
                print(f"   • {issue}")
            if len(issues_found) > 20:
                print(f"   • ... and {len(issues_found) - 20} more issues")
        else:
            print(f"\n✅ No obvious syntax issues found")
        
        # Check if expandAll function is defined
        if 'function expandAll' in rendered_js:
            print(f"\n✅ expandAll function is defined")
        else:
            print(f"\n❌ expandAll function is NOT defined")
            
        if 'function collapseAll' in rendered_js:
            print(f"✅ collapseAll function is defined")
        else:
            print(f"❌ collapseAll function is NOT defined")
            
        if 'function toggleGroup' in rendered_js:
            print(f"✅ toggleGroup function is defined")
        else:
            print(f"❌ toggleGroup function is NOT defined")
        
        return len(issues_found) == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    find_remaining_errors()
