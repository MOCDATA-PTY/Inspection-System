#!/usr/bin/env python3
"""
Test Complete OneDrive Folder Structure Creation
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.onedrive_direct_service import OneDriveDirectUploadService

def test_complete_structure():
    """Test complete OneDrive folder structure creation."""
    print("🧪 Testing Complete OneDrive Folder Structure Creation")
    print("=" * 70)
    
    try:
        # Initialize OneDrive service
        service = OneDriveDirectUploadService()
        
        # Authenticate
        if not service.authenticate_onedrive():
            print("❌ OneDrive authentication failed")
            return False
        
        print("✅ OneDrive authentication successful!")
        
        # Test complete structure creation
        year_folder = "2025"
        month_folder = "September"
        client_folder = "Test_Client_Complete"
        
        print(f"\n📁 Testing complete structure creation for:")
        print(f"   Year: {year_folder}")
        print(f"   Month: {month_folder}")
        print(f"   Client: {client_folder}")
        
        success = service.create_complete_compliance_structure(year_folder, month_folder, client_folder)
        
        if success:
            print("✅ Complete folder structure created successfully!")
            print("\n📋 Expected folder structure:")
            print("Legal-System-Media/inspection/2025/September/Test_Client_Complete/")
            print("├── rfi/")
            print("├── invoice/")
            print("├── lab/")
            print("├── retest/")
            print("└── Compliance/")
            print("    ├── RAW/")
            print("    ├── PMP/")
            print("    ├── POULTRY/")
            print("    └── EGGS/")
            return True
        else:
            print("❌ Complete folder structure creation failed")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_structure()
    if success:
        print("\n🎉 Complete OneDrive folder structure test passed!")
    else:
        print("\n❌ Complete OneDrive folder structure test failed")
