#!/usr/bin/env python3
"""
Debug expand button functionality
"""

import requests
from bs4 import BeautifulSoup
import time

def debug_expand_buttons():
    """Debug expand button functionality"""
    print("🔍 Debugging expand button functionality...")
    
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
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for expand buttons
            expand_buttons = soup.find_all('button', class_='expand-btn')
            print(f"📊 Found {len(expand_buttons)} expand buttons")
            
            if len(expand_buttons) > 0:
                first_button = expand_buttons[0]
                print(f"📋 First expand button:")
                print(f"    Classes: {first_button.get('class', [])}")
                print(f"    Data-group-id: {first_button.get('data-group-id', 'None')}")
                print(f"    HTML: {str(first_button)[:100]}...")
                
                # Check if it has an icon
                icon = first_button.find('i')
                if icon:
                    print(f"    Icon classes: {icon.get('class', [])}")
                else:
                    print("    ❌ No icon found")
            
            # Check for detail rows
            detail_rows = soup.find_all('tr', class_='detail-row')
            print(f"📊 Found {len(detail_rows)} detail rows")
            
            if len(detail_rows) > 0:
                first_detail = detail_rows[0]
                print(f"📋 First detail row:")
                print(f"    ID: {first_detail.get('id', 'None')}")
                print(f"    Style: {first_detail.get('style', 'None')}")
                print(f"    Classes: {first_detail.get('class', [])}")
            
            # Check for group rows
            group_rows = soup.find_all('tr', class_='group-row')
            print(f"📊 Found {len(group_rows)} group rows")
            
            if len(group_rows) > 0:
                first_group = group_rows[0]
                print(f"📋 First group row:")
                print(f"    Data-group-id: {first_group.get('data-group-id', 'None')}")
                print(f"    Classes: {first_group.get('class', [])}")
            
            # Check for expand all button
            expand_all_buttons = soup.find_all('button', {'onclick': 'expandAll()'})
            print(f"📊 Found {len(expand_all_buttons)} expand all buttons")
            
            if len(expand_all_buttons) > 0:
                print("✅ Expand all button found")
            else:
                print("❌ No expand all button found")
                
                # Look for any button with expandAll in onclick
                all_buttons = soup.find_all('button')
                for button in all_buttons:
                    onclick = button.get('onclick', '')
                    if 'expandAll' in onclick:
                        print(f"Found button with expandAll: {onclick}")
            
            # Check JavaScript functions
            scripts = soup.find_all('script')
            js_content = ""
            for script in scripts:
                if script.string:
                    js_content += script.string + "\n"
            
            # Check for specific functions
            functions_to_check = [
                'function expandAll',
                'function collapseAll', 
                'function toggleGroup',
                'function setupExpandButtons',
                'function handleExpandClick'
            ]
            
            print("\n🔍 JavaScript functions:")
            for func in functions_to_check:
                if func in js_content:
                    print(f"    ✅ {func}")
                else:
                    print(f"    ❌ {func}")
            
            # Check for event listeners
            if 'addEventListener' in js_content:
                print("    ✅ addEventListener found")
            else:
                print("    ❌ addEventListener not found")
                
            # Check for DOMContentLoaded
            if 'DOMContentLoaded' in js_content:
                print("    ✅ DOMContentLoaded found")
            else:
                print("    ❌ DOMContentLoaded not found")
            
            return True
        else:
            print(f"❌ Failed to access page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    debug_expand_buttons()
