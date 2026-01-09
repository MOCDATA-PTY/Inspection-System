"""
Test the list_client_folder_files endpoint locally
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import RequestFactory
from main.views.core_views import list_client_folder_files

print("=" * 100)
print("TESTING list_client_folder_files() ENDPOINT")
print("=" * 100)
print()

# Create a fake request
factory = RequestFactory()
request_data = {
    'client_name': 'Roots Butchery Tzaneen',
    'inspection_date': '2025-11-07',
    'force_refresh': True
}

request = factory.post(
    '/list-client-folder-files/',
    data=json.dumps(request_data),
    content_type='application/json'
)

print("Request data:")
print(f"  Client: {request_data['client_name']}")
print(f"  Date: {request_data['inspection_date']}")
print()

# Call the view
response = list_client_folder_files(request)

# Parse response
response_data = json.loads(response.content)

print("=" * 100)
print("RESPONSE")
print("=" * 100)
print()

if response_data.get('success'):
    files = response_data.get('files', {})

    print(f"Success: {response_data['success']}")
    print(f"Total categories: {len(files)}")
    print()

    for category, file_list in files.items():
        print(f"{category}: {len(file_list)} files")
        if file_list:
            for file_dict in file_list[:3]:
                print(f"  - {file_dict.get('name', 'N/A')}")
            if len(file_list) > 3:
                print(f"  ... and {len(file_list) - 3} more files")
        print()

    # Check compliance specifically
    if 'compliance' in files:
        print("=" * 100)
        print("COMPLIANCE FILES DETAIL")
        print("=" * 100)
        print()

        compliance_files = files['compliance']
        print(f"Total: {len(compliance_files)} files")
        print()

        for file_dict in compliance_files:
            print(f"  ✓ {file_dict.get('name')} ({file_dict.get('size')} bytes)")
            print(f"    URL: {file_dict.get('url')}")
            print()
    else:
        print("WARNING: No compliance files in response!")
else:
    print(f"ERROR: {response_data.get('error')}")

print("=" * 100)
print("TEST COMPLETE")
print("=" * 100)
