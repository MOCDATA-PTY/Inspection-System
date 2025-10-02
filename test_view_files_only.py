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
import json

User = get_user_model()

print("="*60)
print("TESTING VIEW FILES ENDPOINT")
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

# Test view files endpoint
client = Client()
client.force_login(test_user)

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

print(f"Response status: {response.status_code}")

if response.status_code != 200:
    print(f"ERROR: View files failed with status {response.status_code}")
    print(f"Response content: {response.content}")
    sys.exit(1)

result = json.loads(response.content)
print(f"Success: {result.get('success', False)}")

if not result.get('success'):
    print(f"ERROR: {result.get('error', 'Unknown error')}")
    sys.exit(1)

files = result.get('files', {})
print(f"\nFiles found:")
for category, file_list in files.items():
    print(f"  {category}: {len(file_list)} files")
    for i, f in enumerate(file_list, 1):
        print(f"    {i}. {f.get('name', 'Unknown')} ({f.get('size', 0)} bytes)")

rfi_files = files.get('rfi', [])
print(f"\nRFI files: {len(rfi_files)}")

if rfi_files:
    print("SUCCESS: RFI files are visible in View Files!")
else:
    print("WARNING: No RFI files found in View Files")

print("="*60 + "\n")
