#!/usr/bin/env python
"""
Test script to debug why files aren't showing in the view files modal
"""
import os
import sys
import django
import json

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# Setup Django
django.setup()

def test_endpoint_response():
    """Test what the endpoint actually returns"""
    print("🧪 TESTING FILE DISPLAY ISSUE")
    print("=" * 60)
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        
        client = Client()
        
        # Create/login test user
        try:
            user = User.objects.create_user(username='testuser', password='testpass')
        except:
            pass
        client.login(username='testuser', password='testpass')
        
        # Test with a real client that has files
        test_data = {
            'client_name': 'Alex Savemor',  # From the logs, this client has files
            'inspection_date': '2025-09-23'
        }
        
        print(f"🔍 Testing with: {test_data}")
        
        response = client.post(
            '/list-client-folder-files/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            print(f"📊 Response Structure:")
            print(f"   Success: {response_data.get('success')}")
            print(f"   Base Path: {response_data.get('base_path')}")
            print(f"   Files Keys: {list(response_data.get('files', {}).keys())}")
            
            files = response_data.get('files', {})
            total_files = sum(len(file_list) for file_list in files.values())
            print(f"   Total Files Found: {total_files}")
            
            # Show detailed file structure
            for category, file_list in files.items():
                print(f"\n📂 Category '{category}': {len(file_list)} files")
                for i, file_info in enumerate(file_list):
                    print(f"   File {i+1}: {file_info}")
            
            # Test what JavaScript expects
            print(f"\n🔍 JavaScript Compatibility Check:")
            print(f"   Expected 'success': {response_data.get('success')}")
            print(f"   Expected 'files' object: {'files' in response_data}")
            
            if total_files == 0:
                print("⚠️  NO FILES FOUND - This explains why the modal is empty!")
                print("   Possible causes:")
                print("   1. Files are in different folder structure")
                print("   2. Client name doesn't match folder name exactly")
                print("   3. Date folder structure is different")
                print("   4. Files are in different document type folders")
            else:
                print("✅ Files found - issue might be in JavaScript display logic")
        else:
            print(f"❌ Request failed: {response.content}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def check_file_structure():
    """Check actual file structure on disk"""
    print(f"\n🗂️  CHECKING ACTUAL FILE STRUCTURE")
    print("=" * 60)
    
    try:
        from django.conf import settings
        
        # Check the media folder structure
        inspection_path = os.path.join(settings.MEDIA_ROOT, 'inspection', '2025', 'September')
        print(f"📁 Base inspection path: {inspection_path}")
        
        if os.path.exists(inspection_path):
            print("✅ Base path exists")
            
            # List client folders
            client_folders = [d for d in os.listdir(inspection_path) if os.path.isdir(os.path.join(inspection_path, d))]
            print(f"📂 Client folders found: {len(client_folders)}")
            
            # Check a specific client
            alex_path = os.path.join(inspection_path, 'Alex Savemor')
            if os.path.exists(alex_path):
                print(f"\n✅ Alex Savemor folder exists: {alex_path}")
                
                # List document type folders
                doc_folders = os.listdir(alex_path)
                print(f"📂 Document folders: {doc_folders}")
                
                # Check each document folder for files
                for doc_folder in doc_folders:
                    doc_path = os.path.join(alex_path, doc_folder)
                    if os.path.isdir(doc_path):
                        try:
                            files = [f for f in os.listdir(doc_path) if os.path.isfile(os.path.join(doc_path, f))]
                            print(f"   📄 {doc_folder}: {len(files)} files")
                            if files:
                                print(f"      Files: {files}")
                        except Exception as e:
                            print(f"   ❌ Error reading {doc_folder}: {e}")
            else:
                print(f"❌ Alex Savemor folder not found")
                print(f"Available folders: {client_folders[:10]}")  # Show first 10
        else:
            print(f"❌ Base path doesn't exist: {inspection_path}")
            
    except Exception as e:
        print(f"❌ File structure check failed: {e}")

def main():
    print("🎯 FILE DISPLAY DEBUG TOOL")
    print("=" * 80)
    
    test_endpoint_response()
    check_file_structure()
    
    print(f"\n💡 TROUBLESHOOTING TIPS:")
    print("1. Check if files exist in the expected folder structure")
    print("2. Verify client name matches folder name exactly")
    print("3. Check if JavaScript is parsing the response correctly")
    print("4. Look for console errors in browser dev tools")
    print("5. Check if modal HTML elements exist on the page")

if __name__ == "__main__":
    main()
