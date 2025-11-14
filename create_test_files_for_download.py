#!/usr/bin/env python3
"""
Create test files for download functionality testing
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def create_test_file_structure():
    """Create test file structure for download testing"""
    print("📁 Creating test file structure for download functionality")
    print("=" * 60)
    
    from django.conf import settings
    
    # Base paths
    media_root = settings.MEDIA_ROOT
    inspection_base = os.path.join(media_root, 'inspection')
    
    # Create year/month structure
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    year_folder = os.path.join(inspection_base, str(current_year))
    month_folder = os.path.join(year_folder, f"{current_month:02d}")
    
    # Create directories
    os.makedirs(month_folder, exist_ok=True)
    print(f"✅ Created folder: {month_folder}")
    
    # Create test client folder
    test_client_folder = os.path.join(month_folder, "Test_Compliance_Client")
    os.makedirs(test_client_folder, exist_ok=True)
    print(f"✅ Created client folder: {test_client_folder}")
    
    # Create subfolders for different file types
    subfolders = ['rfi', 'invoice', 'lab results', 'retest', 'Compliance']
    for subfolder in subfolders:
        subfolder_path = os.path.join(test_client_folder, subfolder)
        os.makedirs(subfolder_path, exist_ok=True)
        print(f"✅ Created subfolder: {subfolder}")
    
    # Create test files
    test_files = [
        ('rfi', 'test_rfi_document.pdf'),
        ('invoice', 'test_invoice.xlsx'),
        ('lab results', 'test_lab_results.pdf'),
        ('retest', 'test_retest_document.pdf'),
        ('Compliance', 'test_compliance_document.pdf')
    ]
    
    for folder, filename in test_files:
        file_path = os.path.join(test_client_folder, folder, filename)
        with open(file_path, 'w') as f:
            f.write(f"Test content for {filename}\nCreated on {datetime.now()}")
        print(f"✅ Created test file: {filename}")
    
    print(f"\n🎉 Test file structure created successfully!")
    print(f"📁 Base path: {test_client_folder}")
    
    return test_client_folder

if __name__ == "__main__":
    try:
        create_test_file_structure()
    except Exception as e:
        print(f"❌ Error creating test files: {e}")
        import traceback
        traceback.print_exc()
