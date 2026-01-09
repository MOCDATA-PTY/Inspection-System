#!/usr/bin/env python3
"""
Test script for automatic ZIP file organization functionality.
This script creates a test ZIP file and tests the auto-organization feature.
"""

import os
import sys
import django
import zipfile
import tempfile
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.views.core_views import organize_zip_file_automatically

def create_test_zip():
    """Create a test ZIP file with files that have inspection numbers."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Create test files with inspection numbers
    test_files = [
        "RAW-Label-RE-COR-PLT-JWY-4641-Jwayelani Pine Town-8629.pdf",
        "RAW-Label-RE-COR-PLT-JWY-4641-Jwayelani Pine Town-8630.pdf", 
        "RAW-Label-RE-COR-PLT-JWY-4641-Jwayelani Pine Town-8631.pdf",
        "RAW-Dir-RE-COR-PLT-JWY-4641-Jwayelani Pine Town-7242.pdf",  # No inspection number
        "RAW-Dir-RE-COR-PLT-JWY-4641-Jwayelani Pine Town-7243.pdf",  # No inspection number
    ]
    
    # Create test files
    for filename in test_files:
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w') as f:
            f.write(f"Test content for {filename}")
    
    # Create ZIP file
    zip_path = os.path.join(temp_dir, "test_compliance_files.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in test_files:
            file_path = os.path.join(temp_dir, filename)
            zipf.write(file_path, filename)
    
    return zip_path

def test_auto_organization():
    """Test the automatic ZIP file organization."""
    print("🧪 Testing automatic ZIP file organization...")
    
    try:
        # Create test ZIP file
        zip_path = create_test_zip()
        print(f"✅ Created test ZIP file: {zip_path}")
        
        # Test the organization function
        organize_zip_file_automatically(
            zip_path, 
            "Jwayelani Pine Town", 
            "2025-09-11", 
            "POULTRY"
        )
        
        print("✅ Auto-organization test completed successfully!")
        
        # Check if individual inspection folders were created
        base_dir = os.path.dirname(zip_path)
        inspection_folders = [d for d in os.listdir(base_dir) if d.startswith('inspection-')]
        print(f"📁 Created inspection folders: {inspection_folders}")
        
        # Check if general files were moved
        general_files = [f for f in os.listdir(base_dir) if f.endswith('.pdf')]
        print(f"📄 General files: {general_files}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auto_organization()
