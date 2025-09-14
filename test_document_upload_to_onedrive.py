#!/usr/bin/env python3
"""
Test OneDrive Upload for RFI, LAB, and other document types
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

def test_document_upload_to_onedrive():
    """Test uploading different document types to OneDrive."""
    print("🧪 Testing OneDrive Upload for RFI, LAB, and other documents")
    print("=" * 70)
    
    try:
        # Initialize OneDrive service
        service = OneDriveDirectUploadService()
        
        # Authenticate
        if not service.authenticate_onedrive():
            print("❌ OneDrive authentication failed")
            return False
        
        print("✅ OneDrive authentication successful!")
        
        # Test parameters
        year_folder = "2025"
        month_folder = "September"
        client_folder = "Test_Client_Documents"
        
        # Create test file content
        test_content = b"This is a test document for OneDrive upload testing."
        
        # Test different document types
        document_types = [
            ('rfi', 'Test_RFI_Document.pdf'),
            ('invoice', 'Test_Invoice_Document.pdf'),
            ('lab', 'Test_Lab_Report.pdf'),
            ('retest', 'Test_Retest_Document.pdf')
        ]
        
        print(f"\n📁 Testing document uploads for client: {client_folder}")
        
        for doc_type, filename in document_types:
            print(f"\n📤 Testing {doc_type.upper()} upload...")
            
            # Create the complete folder structure
            service.create_complete_compliance_structure(year_folder, month_folder, client_folder)
            
            # Build OneDrive path
            onedrive_base = getattr(django.conf.settings, 'ONEDRIVE_FOLDER', 'FoodSafety Agency Inspections')
            
            if doc_type in ['lab']:
                # For lab documents, use commodity subfolder
                commodity = "RAW"  # Test commodity
                onedrive_path = f"{onedrive_base}/inspection/{year_folder}/{month_folder}/{client_folder}/lab/{commodity}/{filename}"
            else:
                # For other document types, use standard folder
                onedrive_path = f"{onedrive_base}/inspection/{year_folder}/{month_folder}/{client_folder}/{doc_type}/{filename}"
            
            # Upload to OneDrive
            success = service.upload_to_onedrive_direct(test_content, onedrive_path)
            
            if success:
                print(f"✅ {doc_type.upper()} uploaded successfully: {filename}")
            else:
                print(f"❌ {doc_type.upper()} upload failed: {filename}")
        
        print("\n📋 Expected OneDrive structure:")
        print(f"FoodSafety Agency Inspections/inspection/{year_folder}/{month_folder}/{client_folder}/")
        print("├── rfi/")
        print("│   └── Test_RFI_Document.pdf")
        print("├── invoice/")
        print("│   └── Test_Invoice_Document.pdf")
        print("├── lab/")
        print("│   └── RAW/")
        print("│       └── Test_Lab_Report.pdf")
        print("├── retest/")
        print("│   └── Test_Retest_Document.pdf")
        print("└── Compliance/")
        print("    ├── RAW/")
        print("    ├── PMP/")
        print("    ├── POULTRY/")
        print("    └── EGGS/")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_document_upload_to_onedrive()
    if success:
        print("\n🎉 OneDrive document upload test completed!")
    else:
        print("\n❌ OneDrive document upload test failed")
