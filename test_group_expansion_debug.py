#!/usr/bin/env python3
"""
Test script to debug group expansion issue on inspections page
"""

import requests
from bs4 import BeautifulSoup
import re

def test_group_expansion():
    """Test the group expansion functionality"""
    print("🔍 Testing group expansion on inspections page...")
    
    try:
        # Make request to inspections page
        response = requests.get('http://127.0.0.1:8000/inspections/', timeout=30)
        
        if response.status_code == 200:
            print("✅ Successfully loaded inspections page")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for expand buttons
            expand_buttons = soup.find_all('button', class_='expand-btn')
            print(f"📊 Found {len(expand_buttons)} expand buttons")
            
            # Check for detail rows
            detail_rows = soup.find_all('tr', class_='detail-row')
            print(f"📊 Found {len(detail_rows)} detail rows")
            
            # Check for group rows
            group_rows = soup.find_all('tr', class_='group-row')
            print(f"📊 Found {len(group_rows)} group rows")
            
            # Check JavaScript functions
            scripts = soup.find_all('script')
            js_content = ""
            for script in scripts:
                if script.string:
                    js_content += script.string + "\n"
            
            # Check for toggleGroup function
            if 'function toggleGroup' in js_content:
                print("✅ toggleGroup function found")
            else:
                print("❌ toggleGroup function NOT found")
            
            # Check for setupExpandButtons function
            if 'function setupExpandButtons' in js_content:
                print("✅ setupExpandButtons function found")
            else:
                print("❌ setupExpandButtons function NOT found")
            
            # Check for event listeners
            if 'addEventListener' in js_content:
                print("✅ Event listeners found")
            else:
                print("❌ Event listeners NOT found")
            
            # Check for console.log statements
            console_logs = re.findall(r'console\.log\([^)]+\)', js_content)
            print(f"📊 Found {len(console_logs)} console.log statements")
            
            # Look for specific issues
            if 'console.log(\'Toggling group:\', groupId);' in js_content:
                print("✅ Missing console.log line found in toggleGroup")
            else:
                print("❌ Missing console.log line NOT found - this might be the issue")
            
            # Check if detail rows have proper IDs
            for i, detail_row in enumerate(detail_rows[:3]):  # Check first 3
                row_id = detail_row.get('id', '')
                if row_id.startswith('detail-'):
                    print(f"✅ Detail row {i+1} has proper ID: {row_id}")
                else:
                    print(f"❌ Detail row {i+1} missing proper ID: {row_id}")
            
            # Check if expand buttons have proper data-group-id
            for i, button in enumerate(expand_buttons[:3]):  # Check first 3
                group_id = button.get('data-group-id', '')
                if group_id:
                    print(f"✅ Expand button {i+1} has group ID: {group_id}")
                else:
                    print(f"❌ Expand button {i+1} missing group ID")
            
            return True
            
        else:
            print(f"❌ Failed to load inspections page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing group expansion: {e}")
        return False

if __name__ == "__main__":
    test_group_expansion()
