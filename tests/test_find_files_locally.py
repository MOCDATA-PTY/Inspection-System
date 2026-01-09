"""
Test finding compliance files locally with the fake data we created
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from pathlib import Path

print("=" * 100)
print("FINDING FAKE COMPLIANCE FILES LOCALLY")
print("=" * 100)
print()

client_name = "Roots Butchery Tzaneen"
inspection_date = "2025-11-07"

# Build paths
media_root = Path(settings.MEDIA_ROOT)
base_path = media_root / "inspection" / "2025" / "November"

print(f"Media root: {media_root}")
print(f"Base path: {base_path}")
print(f"Base path exists: {base_path.exists()}")
print()

# Check what folders exist in November
if base_path.exists():
    print("Folders in November 2025:")
    print("-" * 100)
    for item in base_path.iterdir():
        if item.is_dir():
            print(f"  - {item.name}/")
    print()

# Check the specific client folder
client_path = base_path / client_name
print(f"Client path: {client_path}")
print(f"Client path exists: {client_path.exists()}")
print()

if client_path.exists():
    print("Contents of client folder:")
    print("-" * 100)
    for item in client_path.iterdir():
        if item.is_dir():
            print(f"  - {item.name}/ (folder)")
    print()

    # Check Inspection-2784 folder
    inspection_folder = client_path / "Inspection-2784"
    if inspection_folder.exists():
        print("Contents of Inspection-2784:")
        print("-" * 100)
        for item in inspection_folder.iterdir():
            if item.is_dir():
                print(f"  - {item.name}/ (folder)")
        print()

        # Check Compliance folder (both cases)
        compliance_caps = inspection_folder / "Compliance"
        compliance_lower = inspection_folder / "compliance"

        print(f"'Compliance' (caps) exists: {compliance_caps.exists()}")
        print(f"'compliance' (lower) exists: {compliance_lower.exists()}")
        print()

        # Show Compliance folder contents
        if compliance_caps.exists():
            print("Contents of Compliance folder:")
            print("-" * 100)

            # Count total files
            all_pdfs = list(compliance_caps.rglob('*.pdf'))
            print(f"Total PDF files: {len(all_pdfs)}")
            print()

            # Show by subfolder
            for subfolder in compliance_caps.iterdir():
                if subfolder.is_dir():
                    pdfs = list(subfolder.glob('*.pdf'))
                    print(f"  {subfolder.name}/ ({len(pdfs)} PDFs):")
                    for pdf in pdfs:
                        size_bytes = pdf.stat().st_size
                        print(f"    - {pdf.name} ({size_bytes} bytes)")
                    print()

print()
print("=" * 100)
print("NOW TESTING WITH list_client_folder_files() ENDPOINT")
print("=" * 100)
print()

# Test the endpoint
import json
from django.test import RequestFactory
from main.views.core_views import list_client_folder_files

factory = RequestFactory()
request_data = {
    'client_name': client_name,
    'inspection_date': inspection_date,
    'force_refresh': True
}

request = factory.post(
    '/list-client-folder-files/',
    data=json.dumps(request_data),
    content_type='application/json'
)

response = list_client_folder_files(request)
response_data = json.loads(response.content)

if response_data.get('success'):
    files = response_data.get('files', {})

    print(f"SUCCESS! Found {len(files)} categories")
    print()

    for category, file_list in files.items():
        if len(file_list) > 0:
            print(f"{category}: {len(file_list)} files")
            for file_dict in file_list:
                print(f"  - {file_dict.get('name')} ({file_dict.get('size')} bytes)")
            print()
else:
    print(f"ERROR: {response_data.get('error')}")

print()
print("=" * 100)
print("DONE")
print("=" * 100)
