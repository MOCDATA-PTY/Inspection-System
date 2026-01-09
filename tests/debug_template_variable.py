#!/usr/bin/env python3
"""
Debug template variable that might be causing JavaScript syntax error
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_template_variable():
    """Debug template variable causing JavaScript syntax error"""
    print("🔍 Debugging template variable...")
    
    session = requests.Session()
    
    try:
        # Login
        login_page = session.get('http://127.0.0.1:8000/login/')
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'}).get('value')
        
        login_data = {
            'username': 'developer',
            'password': 'Dev2025!',
            'csrfmiddlewaretoken': csrf_token
        }
        
        session.post('http://127.0.0.1:8000/login/', data=login_data)
        
        # Get inspections page
        response = session.get('http://127.0.0.1:8000/inspections/')
        
        if response.status_code == 200:
            # Look for the specific line that's causing the error
            content = response.text
            
            # Find the line with totalRecords
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'totalRecords' in line:
                    print(f"Line {i+1}: {line}")
                    
                    # Check if there are any syntax issues
                    if '{{' in line and '}}' in line:
                        print("⚠️ Template variable found in JavaScript")
                        
                        # Extract the template variable
                        match = re.search(r'\{\{.*?\}\}', line)
                        if match:
                            template_var = match.group(0)
                            print(f"Template variable: {template_var}")
                            
                            # Check if it's properly formatted
                            if '|default:0' in template_var:
                                print("✅ Has default value")
                            else:
                                print("❌ Missing default value")
            
            # Look for any unclosed braces or syntax issues
            js_start = content.find('<script>')
            js_end = content.rfind('</script>')
            
            if js_start != -1 and js_end != -1:
                js_content = content[js_start:js_end]
                
                # Count braces
                open_braces = js_content.count('{')
                close_braces = js_content.count('}')
                
                print(f"📊 JavaScript braces: {open_braces} open, {close_braces} close")
                
                if open_braces != close_braces:
                    print("❌ Mismatched braces!")
                    
                    # Find the problematic area
                    lines = js_content.split('\n')
                    for i, line in enumerate(lines):
                        if 'totalRecords' in line:
                            print(f"Problematic line {i+1}: {line}")
                            
                            # Check surrounding lines
                            for j in range(max(0, i-2), min(len(lines), i+3)):
                                print(f"  Line {j+1}: {lines[j]}")
                else:
                    print("✅ Braces are balanced")
            
            return True
        else:
            print(f"❌ Failed to access page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    debug_template_variable()
