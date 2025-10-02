#!/usr/bin/env python3
"""
Debug the single row that's being rendered
"""

import requests
from bs4 import BeautifulSoup
import time

def debug_single_row():
    """Debug the single row"""
    print("🔍 Debugging single row...")
    
    session = requests.Session()
    
    try:
        # Login
        login_page = session.get('http://127.0.0.1:8000/login/')
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'}).get('value')
        
        login_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        session.post('http://127.0.0.1:8000/login/', data=login_data)
        
        # Get inspections page
        response = session.get('http://127.0.0.1:8000/inspections/')
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table
        table = soup.find('table', id='shipmentsTable')
        if table:
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                print(f"📊 Found {len(rows)} rows in tbody")
                
                for i, row in enumerate(rows):
                    print(f"\nRow {i+1}:")
                    print(f"  Classes: {row.get('class', [])}")
                    print(f"  HTML: {str(row)[:200]}...")
                    
                    # Check for any buttons in this row
                    buttons = row.find_all('button')
                    print(f"  Buttons: {len(buttons)}")
                    for j, button in enumerate(buttons):
                        print(f"    Button {j+1}: {button.get('class', [])}")
                    
                    # Check for any cells
                    cells = row.find_all('td')
                    print(f"  Cells: {len(cells)}")
                    for j, cell in enumerate(cells):
                        print(f"    Cell {j+1}: {cell.get_text().strip()[:50]}...")
        else:
            print("❌ No table found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_single_row()
