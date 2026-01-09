#!/usr/bin/env python3
"""
Test specific file retrieval for Jusmar Farm Eggs
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.views.core_views import get_inspection_files_local

def test_direct_path():
    """Test direct path access"""
    print("=" * 80)
    print("🧪 TESTING DIRECT PATH ACCESS")
    print("=" * 80)
    
    client_name = "Jusmar Farm Eggs (Pty) Ltd."
    year = "2025"
    month = "September"
    
    base_path = os.path.join(settings.MEDIA_ROOT, 'inspection', year, month, client_name)
    print(f"📁 Base path: {base_path}")
    print(f"📁 Exists: {os.path.exists(base_path)}")
    
    if os.path.exists(base_path):
        contents = os.listdir(base_path)
        print(f"📁 Contents: {contents}")
        
        rfi_path = os.path.join(base_path, 'Request For Invoice')
        print(f"📁 RFI path: {rfi_path}")
        print(f"📁 RFI exists: {os.path.exists(rfi_path)}")
        
        if os.path.exists(rfi_path):
            rfi_files = os.listdir(rfi_path)
            print(f"📄 RFI files: {rfi_files}")
            
            for file in rfi_files:
                file_path = os.path.join(rfi_path, file)
                size = os.path.getsize(file_path)
                print(f"  - {file} ({size:,} bytes)")
                return True
    
    return False

def test_retrieval_function():
    """Test the actual retrieval function with debug"""
    print("\n" + "=" * 80)
    print("🧪 TESTING RETRIEVAL FUNCTION WITH DEBUG")
    print("=" * 80)
    
    client_name = "Jusmar Farm Eggs (Pty) Ltd."
    inspection_date = "2025-09-18"
    
    print(f"🔍 Calling get_inspection_files_local('{client_name}', '{inspection_date}')")
    
    # Clear cache first
    from django.core.cache import cache
    cache.clear()
    
    files = get_inspection_files_local(client_name, inspection_date)
    
    print(f"\n📊 RESULT: {files}")
    print(f"📊 RFI files found: {len(files.get('rfi', []))}")
    
    if files.get('rfi'):
        for file_info in files['rfi']:
            print(f"  - {file_info}")
    
    return len(files.get('rfi', [])) > 0

def test_path_variations():
    """Test different path variations"""
    print("\n" + "=" * 80)
    print("🧪 TESTING PATH VARIATIONS")
    print("=" * 80)
    
    variations = [
        "Jusmar Farm Eggs (Pty) Ltd.",
        "Jusmar Farm Eggs (Pty) Ltd",
        "Jusmar Farm Eggs Pty Ltd",
        "Jusmar Farm Eggs Pty Ltd."
    ]
    
    for client_name in variations:
        print(f"\n🔍 Testing: '{client_name}'")
        base_path = os.path.join(settings.MEDIA_ROOT, 'inspection', '2025', 'September', client_name)
        exists = os.path.exists(base_path)
        print(f"📁 Path exists: {exists}")
        
        if exists:
            try:
                contents = os.listdir(base_path)
                print(f"📁 Contents: {contents}")
                
                rfi_path = os.path.join(base_path, 'Request For Invoice')
                if os.path.exists(rfi_path):
                    rfi_files = os.listdir(rfi_path)
                    print(f"📄 RFI files: {rfi_files}")
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    print("🚀 TESTING SPECIFIC FILE RETRIEVAL FOR JUSMAR FARM EGGS")
    
    # Test 1: Direct path access
    direct_success = test_direct_path()
    
    # Test 2: Retrieval function
    retrieval_success = test_retrieval_function()
    
    # Test 3: Path variations
    test_path_variations()
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Direct path access: {'✅ SUCCESS' if direct_success else '❌ FAILED'}")
    print(f"Retrieval function: {'✅ SUCCESS' if retrieval_success else '❌ FAILED'}")
    
    if direct_success and not retrieval_success:
        print("🔍 FILES EXIST BUT RETRIEVAL FUNCTION FAILS - INVESTIGATING...")

if __name__ == "__main__":
    main()
