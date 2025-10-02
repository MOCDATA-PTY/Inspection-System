#!/usr/bin/env python3
"""
Test inspections page with proper authentication
"""

import requests
from bs4 import BeautifulSoup

def test_with_login():
    """Test the inspections page with proper authentication"""
    print("🔍 Testing inspections page with authentication...")
    
    session = requests.Session()
    
    try:
        # First, get the login page to get CSRF token
        login_page = session.get('http://127.0.0.1:8000/login/')
        
        if login_page.status_code != 200:
            print(f"❌ Failed to get login page: {login_page.status_code}")
            return False
            
        # Parse login page to get CSRF token
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = None
        
        # Look for CSRF token in form
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
            print("✅ Found CSRF token")
        else:
            print("❌ No CSRF token found")
            return False
            
        # Login with test credentials
        login_data = {
            'username': 'admin',  # Try common admin username
            'password': 'admin',  # Try common admin password
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post('http://127.0.0.1:8000/login/', data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Login attempt completed")
            
            # Check if we're still on login page (failed) or redirected
            if 'login' in login_response.url.lower():
                print("❌ Login failed - still on login page")
                
                # Try to find error messages
                soup = BeautifulSoup(login_response.text, 'html.parser')
                error_messages = soup.find_all('div', class_='error-message')
                if error_messages:
                    for error in error_messages:
                        print(f"    Error: {error.get_text().strip()}")
                
                return False
            else:
                print("✅ Login successful - redirected")
        else:
            print(f"❌ Login failed with status: {login_response.status_code}")
            return False
            
        # Now try to access the inspections page
        inspections_response = session.get('http://127.0.0.1:8000/inspections/')
        
        if inspections_response.status_code == 200:
            print("✅ Successfully accessed inspections page")
            
            # Parse the inspections page
            soup = BeautifulSoup(inspections_response.text, 'html.parser')
            
            # Check for table structure
            table = soup.find('table', id='shipmentsTable')
            if table:
                print("✅ Table structure found")
                
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    print(f"📊 Found {len(rows)} rows in tbody")
                    
                    if len(rows) > 0:
                        print("✅ Data rows found!")
                        
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
                            print("✅ Group expansion structure is present!")
                            return True
                        else:
                            print("❌ Group expansion structure is missing")
                            return False
                    else:
                        print("❌ No data rows found")
                        return False
                else:
                    print("❌ No tbody found")
                    return False
            else:
                print("❌ No table structure found")
                return False
        else:
            print(f"❌ Failed to access inspections page: {inspections_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_with_login()
