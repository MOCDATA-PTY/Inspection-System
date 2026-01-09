import os
import django
import sys
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

print("\n" + "="*80)
print("TESTING: Royal Butchery - UnionDale - 2025-11-11")
print("="*80 + "\n")

# Test 1: Check filesystem
print("TEST 1: Filesystem Check")
print("-" * 80)

expected_paths = [
    '/root/Inspection-System/media/inspection/2025/November/royal_butchery_uniondale/lab',
    '/root/Inspection-System/media/inspection/2025/November/mobile_royal_butchery_uniondale/lab'
]

files_found = []
for base_path in expected_paths:
    if os.path.exists(base_path):
        print(f"✓ Folder exists: {base_path}")
        for filename in os.listdir(base_path):
            file_path = os.path.join(base_path, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                files_found.append({
                    'path': file_path,
                    'name': filename,
                    'size': file_size
                })
                print(f"  - File: {filename}")
                print(f"    Size: {file_size / 1024:.1f} KB")
                print(f"    Full path: {file_path}")
    else:
        print(f"✗ Folder not found: {base_path}")

if not files_found:
    print("\n✗ ERROR: No lab files found in filesystem!")
    sys.exit(1)

print(f"\n✓ Found {len(files_found)} lab file(s) in filesystem\n")

# Test 2: Test API endpoint
print("TEST 2: API Endpoint Test")
print("-" * 80)

from main.views.core_views import list_client_folder_files
from django.http import QueryDict
from django.test import RequestFactory
from django.contrib.auth.models import User

factory = RequestFactory()

# Create request
request = factory.get('/list-client-folder-files/')
request.user = User.objects.first()

if not request.user:
    print("✗ ERROR: No users found in database!")
    sys.exit(1)

request.GET = QueryDict(mutable=True)
request.GET['client_name'] = 'Royal Butchery - UnionDale'
request.GET['date'] = '2025-11-11'

print(f"API Request Parameters:")
print(f"  client_name: Royal Butchery - UnionDale")
print(f"  date: 2025-11-11")
print()

# Call the view
response = list_client_folder_files(request)

print(f"API Response Status: {response.status_code}")

if response.status_code == 200:
    data = json.loads(response.content)

    print(f"API Success: {data.get('success')}")
    print()

    files = data.get('files', {})
    print(f"File categories returned: {list(files.keys())}")
    print()

    # Check each category
    for category, file_list in files.items():
        if file_list:
            print(f"Category '{category}': {len(file_list)} file(s)")
            for file_info in file_list:
                print(f"  - {file_info.get('name')}")
                print(f"    Type: {file_info.get('document_type')}")
                print(f"    Path: {file_info.get('path')}")

    # Specific lab file check
    lab_files = files.get('lab', [])
    print()
    print("="*80)
    if lab_files:
        print(f"✓ SUCCESS: API returned {len(lab_files)} lab file(s)")
        print()
        for lab_file in lab_files:
            print(f"Lab File Details:")
            print(f"  Name: {lab_file.get('name')}")
            print(f"  Type: {lab_file.get('document_type')}")
            print(f"  Size: {lab_file.get('size', 0) / 1024:.1f} KB")
            print(f"  Path: {lab_file.get('path')}")
            print(f"  URL: {lab_file.get('url')}")
    else:
        print("✗ FAILURE: No lab files returned by API!")
        print()
        print("Files returned in other categories:")
        for category, file_list in files.items():
            if file_list:
                print(f"  {category}: {len(file_list)} files")
                for f in file_list[:3]:
                    print(f"    - {f.get('name')}")

else:
    print(f"✗ API Error: {response.status_code}")
    print(response.content)

print("="*80)

# Test 3: Frontend button state check
print()
print("TEST 3: Expected Frontend Behavior")
print("-" * 80)

if files_found and response.status_code == 200:
    data = json.loads(response.content)
    lab_files = data.get('files', {}).get('lab', [])

    if lab_files:
        print("✓ Lab button SHOULD turn GREEN")
        print("  Reason: API returns lab files in 'lab' category")
    else:
        print("✗ Lab button will stay GREY")
        print("  Reason: API does not return lab files in 'lab' category")
        print("  Issue: Files exist in filesystem but API is not categorizing them correctly")
else:
    print("✗ Lab button will stay GREY")
    print("  Reason: API request failed or no files found")

print()
print("="*80)
print("TEST COMPLETE")
print("="*80)
