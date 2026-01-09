#!/usr/bin/env python3
"""
Test the simplified file naming system
"""
import os
import sys
import django
import re

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection
from datetime import datetime

def create_folder_name(name):
    """Create Linux-friendly folder name - must match upload function"""
    if not name:
        return "unknown_client"
    # Remove special characters, keep only alphanumeric, spaces, hyphens, underscores
    clean_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)
    # Replace spaces and hyphens with underscores
    clean_name = clean_name.replace(' ', '_').replace('-', '_')
    # Remove consecutive underscores
    clean_name = re.sub(r'_+', '_', clean_name)
    # Remove leading/trailing underscores
    clean_name = clean_name.strip('_').lower()
    return clean_name or "unknown_client"

def test_naming_convention():
    """Test the new naming convention"""
    print("=== Testing Simplified File Naming System ===\n")
    
    test_cases = [
        "Meat Mania",
        "Boxer Superstore - Kwamashu 2",
        "Eggbert Eggs (Pty) Ltd - Arendnes",
        "Pick 'n Pay - Burgersfort",
        "SUPERSPAR - City Centre",
        "T/A Something",
        "Client-With-Dashes"
    ]
    
    print("Client Name Sanitization Test:")
    print("-" * 60)
    for client_name in test_cases:
        sanitized = create_folder_name(client_name)
        print(f"  {client_name:40} -> {sanitized}")
    
    print("\n" + "=" * 60)
    print("\nFolder Structure Test:")
    print("-" * 60)
    
    # Test with Meat Mania
    client_name = "Meat Mania"
    inspection_date = "2025-09-26"
    date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
    year_folder = date_obj.strftime('%Y')
    month_folder = date_obj.strftime('%B')
    client_folder = create_folder_name(client_name)
    
    print(f"\nClient: {client_name}")
    print(f"Date: {inspection_date}")
    print(f"\nFolder structure:")
    print(f"  Year: {year_folder}")
    print(f"  Month: {month_folder}")
    print(f"  Client: {client_folder}")
    
    # Build full paths
    base_path = os.path.join(settings.MEDIA_ROOT, 'inspection', year_folder, month_folder, client_folder)
    rfi_path = os.path.join(base_path, 'rfi')
    invoice_path = os.path.join(base_path, 'invoice')
    compliance_path = os.path.join(base_path, 'compliance')
    
    print(f"\nFull paths:")
    print(f"  Base: {base_path}")
    print(f"  RFI: {rfi_path}")
    print(f"  Invoice: {invoice_path}")
    print(f"  Compliance: {compliance_path}")
    
    # Create the structure
    print(f"\nCreating folder structure...")
    os.makedirs(rfi_path, exist_ok=True)
    os.makedirs(invoice_path, exist_ok=True)
    os.makedirs(compliance_path, exist_ok=True)
    
    # Create a test file
    test_file = os.path.join(rfi_path, "test_rfi_20250926_120000.pdf")
    with open(test_file, 'w') as f:
        f.write("Test RFI content")
    
    print(f"  ✓ Created test file: {test_file}")
    print(f"  ✓ File exists: {os.path.exists(test_file)}")
    
    # Test file listing
    print(f"\nListing files in RFI folder:")
    if os.path.exists(rfi_path):
        files = os.listdir(rfi_path)
        for file in files:
            print(f"  - {file}")
    
    print("\n" + "=" * 60)
    print("\n✅ Test Complete!")
    print("\nNext steps:")
    print("1. Start the Django server")
    print("2. Try uploading an RFI for 'Meat Mania' on 2025-09-26")
    print("3. Click 'View Files' to verify it appears")

if __name__ == '__main__':
    test_naming_convention()

