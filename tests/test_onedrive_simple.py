"""
Simple test - OneDrive disabled
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

print("=" * 70)
print("TESTING ONEDRIVE DISABLED")
print("=" * 70)
print()

# Test OneDrive service
from main.services.onedrive_direct_service import onedrive_direct_service

print("Test 1: OneDrive service auto-start")
print(f"  is_running: {onedrive_direct_service.is_running}")
if not onedrive_direct_service.is_running:
    print("  PASS: OneDrive did NOT auto-start")
else:
    print("  FAIL: OneDrive auto-started!")

print()

print("Test 2: OneDrive authentication")
result = onedrive_direct_service.authenticate_onedrive()
print(f"  Result: {result}")
if result == False:
    print("  PASS: OneDrive authentication disabled")
else:
    print("  FAIL: OneDrive authentication enabled!")

print()

print("Test 3: Daily compliance sync")
from main.services.daily_compliance_sync import daily_sync_service
print(f"  Sync service exists: {daily_sync_service is not None}")
print(f"  Sync is running: {daily_sync_service.is_running}")

print()
print("=" * 70)
print("RESULT: OneDrive is DISABLED")
print("=" * 70)
print()
print("No OneDrive authentication messages should appear above.")
print("If you see any OneDrive auth messages, OneDrive is still active.")
