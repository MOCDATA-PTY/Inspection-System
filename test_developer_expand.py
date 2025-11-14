#!/usr/bin/env python3
"""
Test expand functionality with developer account
"""

import requests
from bs4 import BeautifulSoup
import time

def test_developer_expand():
    """Test expand functionality with developer account"""
    print("🔍 Testing expand functionality with developer account...")
    
    # Wait for server to start
    time.sleep(2)
    
    session = requests.Session()
    
    try:
        # Get login page
        login_page = session.get('http://127.0.0.1:8000/login/')
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'}).get('value')
        
        # Login with developer account
        login_data = {
            'username': 'developer',
            'password': 'Dev2025!',
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post('http://127.0.0.1:8000/login/', data=login_data)
        
        if 'login' in login_response.url.lower():
            print("❌ Login failed")
            return False
            
        print("✅ Developer login successful")
        
        # Get inspections page
        inspections_response = session.get('http://127.0.0.1:8000/inspections/')
        
        if inspections_response.status_code == 200:
            soup = BeautifulSoup(inspections_response.text, 'html.parser')
            
            # Check for table structure
            table = soup.find('table', id='shipmentsTable')
            if not table:
                print("❌ No table found")
                return False
                
            tbody = table.find('tbody')
            if not tbody:
                print("❌ No tbody found")
                return False
                
            rows = tbody.find_all('tr')
            print(f"📊 Found {len(rows)} rows")
            
            if len(rows) == 0:
                print("❌ No data rows found")
                return False
                
            # Check for expand buttons
            expand_buttons = soup.find_all('button', class_='expand-btn')
            print(f"📊 Found {len(expand_buttons)} expand buttons")
            
            # Check for detail rows
            detail_rows = soup.find_all('tr', class_='detail-row')
            print(f"📊 Found {len(detail_rows)} detail rows")
            
            # Check for group rows
            group_rows = soup.find_all('tr', class_='group-row')
            print(f"📊 Found {len(group_rows)} group rows")
            
            if len(expand_buttons) > 0 and len(detail_rows) > 0:
                print("✅ Expand functionality structure is present!")
                print("🎉 The expand buttons should work now!")
                print("\nTo test:")
                print("1. Go to http://127.0.0.1:8000/inspections/")
                print("2. Login with: developer / Dev2025!")
                print("3. Click the expand buttons (chevron icons) next to client names")
                return True
            else:
                print("❌ Expand functionality structure is missing")
                return False
        else:
            print(f"❌ Failed to access inspections: {inspections_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_developer_expand()
