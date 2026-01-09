"""Test the sync to verify compliance data is transferred correctly"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.scheduled_sync_service import ScheduledSyncService
from main.models import FoodSafetyAgencyInspection

print("=" * 100)
print("TESTING SYNC WITH COMPLIANCE DATA FIX")
print("=" * 100)

# Show stats before sync
print("\n[BEFORE SYNC]")
total_before = FoodSafetyAgencyInspection.objects.count()
compliant_before = FoodSafetyAgencyInspection.objects.filter(
    is_direction_present_for_this_inspection=False
).count()
non_compliant_before = FoodSafetyAgencyInspection.objects.filter(
    is_direction_present_for_this_inspection=True
).count()

print(f"  Total: {total_before}")
print(f"  Compliant: {compliant_before}")
print(f"  Non-Compliant: {non_compliant_before}")

# Run sync
print("\n[RUNNING SYNC...]")
print("This will fetch data from SQL Server with compliance status...")
sync_service = ScheduledSyncService()
sync_service.sync_sql_server()

# Show stats after sync
print("\n" + "=" * 100)
print("[AFTER SYNC]")
print("=" * 100)

total_after = FoodSafetyAgencyInspection.objects.count()
compliant_after = FoodSafetyAgencyInspection.objects.filter(
    is_direction_present_for_this_inspection=False
).count()
non_compliant_after = FoodSafetyAgencyInspection.objects.filter(
    is_direction_present_for_this_inspection=True
).count()

print(f"\n  Total: {total_after}")
print(f"  Compliant (No Direction): {compliant_after} ({compliant_after/total_after*100:.1f}%)")
print(f"  Non-Compliant (Direction): {non_compliant_after} ({non_compliant_after/total_after*100:.1f}%)")

# Show breakdown by commodity
print(f"\n[BREAKDOWN BY COMMODITY]")
print(f"{'Commodity':<15} {'Total':<10} {'Compliant':<12} {'Non-Compliant':<15} {'Pass Rate':<10}")
print("-" * 100)

for commodity in ['PMP', 'RAW', 'EGGS', 'POULTRY']:
    comm_total = FoodSafetyAgencyInspection.objects.filter(commodity=commodity).count()
    comm_compliant = FoodSafetyAgencyInspection.objects.filter(
        commodity=commodity,
        is_direction_present_for_this_inspection=False
    ).count()
    comm_non_compliant = FoodSafetyAgencyInspection.objects.filter(
        commodity=commodity,
        is_direction_present_for_this_inspection=True
    ).count()

    pass_rate = (comm_compliant/comm_total*100) if comm_total > 0 else 0

    print(f"{commodity:<15} {comm_total:<10} {comm_compliant:<12} {comm_non_compliant:<15} {pass_rate:.1f}%")

# Show some sample non-compliant inspections
print(f"\n[SAMPLE NON-COMPLIANT INSPECTIONS]")
non_compliant_samples = FoodSafetyAgencyInspection.objects.filter(
    is_direction_present_for_this_inspection=True
)[:5]

if non_compliant_samples.exists():
    print(f"\nShowing first 5 non-compliant inspections:")
    for insp in non_compliant_samples:
        print(f"  • {insp.commodity} #{insp.remote_id}: {insp.client_name} on {insp.date_of_inspection}")
else:
    print("\n  No non-compliant inspections found (this would indicate a problem!)")

print("\n" + "=" * 100)
print("EXPECTED RESULT: ~50% compliant, ~50% non-compliant (based on SQL Server data)")
print("=" * 100)
