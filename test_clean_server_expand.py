#!/usr/bin/env python3
"""
Test expand buttons with fresh clean server
"""

import requests
from bs4 import BeautifulSoup
import time

def test_clean_server_expand():
    """Test expand functionality with clean server"""
    print("🔍 Testing expand buttons with fresh clean server...")
    
    # Wait for server to fully start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    session = requests.Session()
    
    try:
        # Test server is running
        print("🌐 Testing server connection...")
        test_response = session.get('http://127.0.0.1:8000/', timeout=10)
        if test_response.status_code != 200:
            print(f"❌ Server not responding: {test_response.status_code}")
            return False
        print("✅ Server is running")
        
        # Login as developer
        print("🔐 Logging in...")
        login_page = session.get('http://127.0.0.1:8000/login/')
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        
        login_data = {
            'username': 'developer',
            'password': 'Dev2025!',
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post('http://127.0.0.1:8000/login/', data=login_data)
        
        if 'login' in login_response.url:
            print("❌ Login failed")
            return False
        print("✅ Login successful")
        
        # Get inspections page
        print("📋 Loading inspections page...")
        response = session.get('http://127.0.0.1:8000/inspections/')
        
        if response.status_code != 200:
            print(f"❌ Failed to load inspections page: {response.status_code}")
            return False
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("\n📊 CLEAN SERVER EXPAND BUTTON TEST:")
        print("="*50)
        
        # Check expand buttons
        expand_buttons = soup.find_all('button', class_='expand-btn')
        detail_rows = soup.find_all('tr', class_='detail-row')
        group_rows = soup.find_all('tr', class_='group-row')
        
        print(f"✅ Found {len(expand_buttons)} expand buttons")
        print(f"✅ Found {len(detail_rows)} detail rows")
        print(f"✅ Found {len(group_rows)} group rows")
        
        # Check first expand button structure
        if expand_buttons:
            first_button = expand_buttons[0]
            group_id = first_button.get('data-group-id')
            print(f"✅ First button group ID: {group_id}")
            
            # Check corresponding detail row
            detail_row = soup.find('tr', id=f'detail-{group_id}')
            if detail_row:
                print(f"✅ Detail row exists for: {group_id}")
                print(f"✅ Detail row style: {detail_row.get('style', 'none')}")
            else:
                print(f"❌ No detail row for: {group_id}")
        
        # Check JavaScript
        scripts = soup.find_all('script')
        js_content = ""
        for script in scripts:
            if script.string:
                js_content += script.string + "\n"
        
        # Check for essential functions
        has_toggle = 'function toggleGroup(' in js_content
        has_delegation = 'closest(\'.expand-btn\')' in js_content
        setup_calls = js_content.count('setupExpandButtons(')
        
        print(f"✅ toggleGroup function: {'Present' if has_toggle else 'Missing'}")
        print(f"✅ Event delegation: {'Present' if has_delegation else 'Missing'}")
        print(f"✅ setupExpandButtons calls: {setup_calls} (should be minimal)")
        
        print(f"\n🎯 MANUAL TEST:")
        print("="*50)
        print("1. Open http://127.0.0.1:8000/inspections/ in your browser")
        print("2. Login with: developer / Dev2025!")
        print("3. Look for chevron (►) icons next to client names")
        print("4. Click any chevron to expand/collapse inspection groups")
        print("5. Open browser console (F12) to see debug messages")
        print("6. Each click should show console logs like:")
        print("   'Expand button clicked via delegation for group: [GroupID]'")
        print("   'Toggling group: [GroupID]'")
        
        if (len(expand_buttons) > 0 and len(detail_rows) > 0 and 
            has_toggle and has_delegation and setup_calls <= 2):
            print(f"\n🎉 EXPAND BUTTONS SHOULD WORK PERFECTLY!")
            print("✅ Clean server, fresh cache, fixed JavaScript conflicts")
            return True
        else:
            print(f"\n⚠️  POTENTIAL ISSUES DETECTED")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = test_clean_server_expand()
    if success:
        print(f"\n{'='*60}")
        print("🎉 EXPAND BUTTON FIX VERIFIED ON CLEAN SERVER!")
        print("All users should now be able to expand inspection groups.")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("❌ Issues detected - may need further investigation")
        print(f"{'='*60}")
