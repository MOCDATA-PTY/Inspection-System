"""Trigger a fresh sync with the fixed compliance code"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

print("=" * 100)
print("TRIGGERING FRESH SYNC WITH COMPLIANCE FIX")
print("=" * 100)

# Import the UPDATED service with the fix
from main.services.scheduled_sync_service import ScheduledSyncService

print("\n[INFO] This will use the FIXED code that includes compliance status")
print("[INFO] Expected result: ~50% compliant, ~50% non-compliant")
print("\nStarting sync...")

service = ScheduledSyncService()
service.sync_sql_server()

print("\n" + "=" * 100)
print("SYNC COMPLETE - Checking results...")
print("=" * 100)

# Show final stats
from main.models import FoodSafetyAgencyInspection

total = FoodSafetyAgencyInspection.objects.count()
compliant = FoodSafetyAgencyInspection.objects.filter(
    is_direction_present_for_this_inspection=False
).count()
non_compliant = FoodSafetyAgencyInspection.objects.filter(
    is_direction_present_for_this_inspection=True
).count()

print(f"\n[FINAL RESULTS]")
print(f"  Total: {total:,}")
print(f"  Compliant: {compliant:,} ({compliant/total*100:.1f}%)")
print(f"  Non-Compliant: {non_compliant:,} ({non_compliant/total*100:.1f}%)")

if non_compliant > 100:
    print("\n[SUCCESS] Compliance data is now syncing correctly!")
else:
    print("\n[ERROR] Still not syncing correctly - investigate further")
