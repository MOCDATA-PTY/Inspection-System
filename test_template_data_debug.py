#!/usr/bin/env python3
"""
Test script to debug template data issues on inspections page
"""

import requests
from bs4 import BeautifulSoup
import re

def test_template_data():
    """Test the template data being passed to inspections page"""
    print("🔍 Testing template data on inspections page...")
    
    try:
        # Make request to inspections page
        response = requests.get('http://127.0.0.1:8000/inspections/', timeout=30)
        
        if response.status_code == 200:
            print("✅ Successfully loaded inspections page")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for any error messages
            error_messages = soup.find_all('div', class_='alert-danger')
            if error_messages:
                print("❌ Error messages found:")
                for error in error_messages:
                    print(f"    {error.get_text().strip()}")
            
            # Check for any debug output in the HTML
            debug_output = soup.find_all(text=re.compile(r'DEBUG|ERROR|WARNING'))
            if debug_output:
                print("🔍 Debug output found:")
                for debug in debug_output[:5]:  # Show first 5
                    print(f"    {debug.strip()}")
            
            # Check if there's any content in the table body
            tbody = soup.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                print(f"📊 Found {len(rows)} rows in tbody")
                
                if len(rows) == 0:
                    print("❌ No rows found in tbody - this is the problem!")
                    
                    # Check if there's a "no data" message
                    no_data_messages = soup.find_all(text=re.compile(r'no.*data|empty|no.*inspections|no.*shipments', re.I))
                    if no_data_messages:
                        print("📝 No data messages found:")
                        for msg in no_data_messages:
                            print(f"    {msg.strip()}")
                else:
                    print("✅ Rows found in tbody")
                    for i, row in enumerate(rows[:3]):  # Check first 3 rows
                        classes = row.get('class', [])
                        print(f"    Row {i+1}: classes={classes}")
                        
                        # Check for expand buttons in this row
                        expand_buttons = row.find_all('button', class_='expand-btn')
                        if expand_buttons:
                            print(f"        Found {len(expand_buttons)} expand buttons")
                        else:
                            print("        No expand buttons found")
            else:
                print("❌ No tbody found in the table")
            
            # Check for pagination
            pagination = soup.find('div', class_='pagination')
            if pagination:
                print("✅ Pagination found")
                page_info = pagination.find_all(text=re.compile(r'Page \d+ of \d+'))
                if page_info:
                    print(f"    {page_info[0].strip()}")
            else:
                print("❌ No pagination found")
            
            # Check for any JavaScript errors in console logs
            scripts = soup.find_all('script')
            js_content = ""
            for script in scripts:
                if script.string:
                    js_content += script.string + "\n"
            
            # Look for specific error patterns
            error_patterns = [
                r'Error.*shipment',
                r'undefined.*shipment',
                r'Cannot read property.*shipment',
                r'TypeError.*shipment'
            ]
            
            for pattern in error_patterns:
                matches = re.findall(pattern, js_content, re.I)
                if matches:
                    print(f"❌ JavaScript errors found: {matches}")
            
            # Check if there are any Django template errors
            template_errors = soup.find_all(text=re.compile(r'TemplateSyntaxError|TemplateDoesNotExist|VariableDoesNotExist'))
            if template_errors:
                print("❌ Template errors found:")
                for error in template_errors:
                    print(f"    {error.strip()}")
            
            return True
            
        else:
            print(f"❌ Failed to load inspections page: {response.status_code}")
            print(f"Response content: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error testing template data: {e}")
        return False

if __name__ == "__main__":
    test_template_data()
