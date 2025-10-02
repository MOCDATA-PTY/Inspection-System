import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from main.models import FoodSafetyAgencyInspection
from datetime import datetime
from io import BytesIO
import json

User = get_user_model()

def create_test_pdf():
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "TEST RFI DOCUMENT")
    p.drawString(100, 730, f"Generated: {datetime.now()}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def check_files_in_folder(folder_path):
    """Check if RFI files exist in the folder"""
    if not os.path.exists(folder_path):
        return []
    
    files = []
    for item in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, item)) and item.lower().endswith('.pdf'):
            files.append(item)
    return files

print("="*60)
print("TESTING RFI UPLOAD AND FILE DETECTION")
print("="*60)

# Get test user
test_user = User.objects.filter(role='inspector').first() or User.objects.filter(role='developer').first()
if not test_user:
    print("ERROR: No test user found")
    sys.exit(1)
print(f"User: {test_user.username}")

# Get inspection
inspection = FoodSafetyAgencyInspection.objects.filter(
    client_name__isnull=False,
    date_of_inspection__isnull=False
).order_by('-date_of_inspection').first()

if not inspection:
    print("ERROR: No inspections found")
    sys.exit(1)

print(f"Client: {inspection.client_name}")
print(f"Date: {inspection.date_of_inspection}")
group_id = f"{inspection.client_name}_{inspection.date_of_inspection.strftime('%Y%m%d')}"
print(f"Group ID: {group_id}")

# Check folder structure before upload
from django.conf import settings
date_obj = inspection.date_of_inspection
year_folder = date_obj.strftime('%Y')
month_folder = date_obj.strftime('%B')
client_folder = inspection.client_name

rfi_folder_path = os.path.join(
    settings.MEDIA_ROOT, 
    'inspection', 
    year_folder, 
    month_folder, 
    client_folder,
    'rfi'
)

print(f"\nRFI folder path: {rfi_folder_path}")
print(f"RFI folder exists: {os.path.exists(rfi_folder_path)}")

if os.path.exists(rfi_folder_path):
    existing_files = check_files_in_folder(rfi_folder_path)
    print(f"Existing RFI files: {existing_files}")
else:
    print("RFI folder does not exist yet")

# Test upload
client = Client()
client.force_login(test_user)

pdf_file = create_test_pdf()
pdf_file.name = f"TEST_RFI_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

print(f"\nUploading RFI: {pdf_file.name}")

# Suppress server output to avoid emoji issues
import logging
logging.disable(logging.CRITICAL)

response = client.post('/upload-document/', {
    'file': pdf_file,
    'group_id': group_id,
    'document_type': 'rfi'
})

logging.disable(logging.NOTSET)

if response.status_code != 200:
    print(f"ERROR: Upload failed with status {response.status_code}")
    sys.exit(1)

result = json.loads(response.content)
if not result.get('success'):
    print(f"ERROR: {result.get('error', 'Unknown error')}")
    sys.exit(1)

print(f"SUCCESS: RFI uploaded to {result.get('file_path')}")

# Check files after upload
print(f"\nAfter upload - RFI folder exists: {os.path.exists(rfi_folder_path)}")
if os.path.exists(rfi_folder_path):
    files_after = check_files_in_folder(rfi_folder_path)
    print(f"RFI files after upload: {files_after}")
    
    if files_after:
        print("SUCCESS: RFI file is visible in the folder!")
    else:
        print("WARNING: No RFI files found in folder")
else:
    print("ERROR: RFI folder still does not exist")

# Test view files endpoint
print(f"\nTesting View Files endpoint...")
response = client.post('/inspections/files/', 
    json.dumps({
        'group_id': group_id,
        'client_name': inspection.client_name,
        'inspection_date': inspection.date_of_inspection.strftime('%Y-%m-%d'),
        '_force_refresh': True
    }),
    content_type='application/json'
)

if response.status_code != 200:
    print(f"ERROR: View files failed with status {response.status_code}")
    sys.exit(1)

result = json.loads(response.content)
if not result.get('success'):
    print(f"ERROR: {result.get('error', 'Unknown error')}")
    sys.exit(1)

files = result.get('files', {})
rfi_files = files.get('rfi', [])

print(f"\nView Files Results:")
print(f"RFI files found: {len(rfi_files)}")
for i, f in enumerate(rfi_files, 1):
    print(f"  {i}. {f.get('name', 'Unknown')} ({f.get('size', 0)} bytes)")

if rfi_files:
    print("\nSUCCESS: RFI file is visible in View Files!")
else:
    print("\nWARNING: RFI not visible in View Files yet")

print("="*60 + "\n")
