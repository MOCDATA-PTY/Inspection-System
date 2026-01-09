#!/usr/bin/env python
"""Check what compliance files exist in Google Drive for specific account codes"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.daily_compliance_sync import DailyComplianceSyncService

print("=" * 80)
print("CHECKING GOOGLE DRIVE COMPLIANCE FILES")
print("=" * 80)

# Create sync service and load files
sync_service = DailyComplianceSyncService()
sync_service.is_running = True

print("\nLoading files from Google Drive...")
file_lookup = sync_service.load_drive_files_standalone()

if not file_lookup:
    print("ERROR: Could not load files from Google Drive!")
    sys.exit(1)

print(f"\nTotal files loaded: {len(file_lookup)}")

# Check for specific account codes
test_account_codes = [
    'RE-IND-EGG-NA-5042',
    'RE-IND-EGG-NA-5053',
]

print("\n" + "-" * 40)
print("SEARCHING FOR TEST ACCOUNT CODES:")
print("-" * 40)

for account_code in test_account_codes:
    print(f"\nSearching for: {account_code}")
    found = False
    for key, file_info in file_lookup.items():
        if file_info['accountCode'] == account_code:
            print(f"  FOUND: {file_info['name']}")
            print(f"    Commodity: {file_info['commodity']}")
            print(f"    Date: {file_info['zipDateStr']}")
            print(f"    URL: {file_info['url']}")
            found = True
    if not found:
        print(f"  NOT FOUND - No compliance document exists for this account code")

# Show sample of what files exist
print("\n" + "-" * 40)
print("SAMPLE OF FILES IN GOOGLE DRIVE (first 20):")
print("-" * 40)

for i, (key, file_info) in enumerate(file_lookup.items()):
    if i >= 20:
        break
    print(f"  {file_info['commodity']}-{file_info['accountCode']}-{file_info['zipDateStr']}")

print("\n" + "=" * 80)
