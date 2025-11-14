#!/usr/bin/env python
"""
Test script for Google Sheets integration
Run this script to test if the Google Sheets service is working correctly
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.google_sheets_service import GoogleSheetsService

def test_google_sheets():
    """Test the Google Sheets service"""
    print("Testing Google Sheets Integration...")
    print("=" * 50)
    
    try:
        # Initialize the service
        service = GoogleSheetsService()
        print("✓ Google Sheets service initialized successfully")
        
        # Test authentication
        print("\nAttempting to authenticate...")
        auth_service = service.authenticate()
        print("✓ Authentication successful")
        
        # Test data fetching
        print("\nFetching data from your spreadsheet...")
        data = service.get_specific_sheet_data()
        
        if data:
            print(f"✓ Successfully fetched {len(data)} rows of data")
            print("\nFirst 5 rows of data:")
            print("-" * 40)
            for i, row in enumerate(data[:5]):
                print(f"Row {row['row_number']}: H='{row['column_h']}' | J='{row['column_j']}'")
            
            if len(data) > 5:
                print(f"... and {len(data) - 5} more rows")
        else:
            print("⚠ No data found in the spreadsheet")
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have placed the 'credentials.json' file in your project root directory")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nCheck the error details above and ensure:")
        print("1. Google Sheets API is enabled in Google Cloud Console")
        print("2. Your credentials.json file is valid")
        print("3. You have access to the spreadsheet")

if __name__ == "__main__":
    test_google_sheets()
