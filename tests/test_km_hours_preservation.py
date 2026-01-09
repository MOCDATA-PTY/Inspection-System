import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 80)
print("KM/HOURS PRESERVATION TEST")
print("=" * 80)

# Check current state
inspections_with_data = FoodSafetyAgencyInspection.objects.filter(
    km_traveled__isnull=False
) | FoodSafetyAgencyInspection.objects.filter(
    hours__isnull=False
)

count = inspections_with_data.count()
print(f"\n[BEFORE] Inspections with km or hours data: {count:,}")

if count > 0:
    print(f"\n[SAMPLE] First 5 inspections with data:")
    for insp in inspections_with_data[:5]:
        print(f"  - ID {insp.remote_id}: {insp.commodity} | {insp.client_name}")
        print(f"    KM: {insp.km_traveled}, Hours: {insp.hours}")
        print(f"    Date: {insp.date_of_inspection}")

# Test update_or_create preservation
print(f"\n" + "=" * 80)
print("TESTING update_or_create PRESERVATION")
print("=" * 80)

# Get a test inspection
test_insp = FoodSafetyAgencyInspection.objects.first()
if test_insp:
    print(f"\n[TEST] Using inspection ID {test_insp.remote_id}")

    # Set test km/hours data
    test_insp.km_traveled = 999
    test_insp.hours = 888
    test_insp.save()
    print(f"[BEFORE] Set km_traveled=999, hours=888")

    # Simulate sync with update_or_create (only updating client_name, NOT km/hours)
    inspection, created = FoodSafetyAgencyInspection.objects.update_or_create(
        commodity=test_insp.commodity,
        remote_id=test_insp.remote_id,
        date_of_inspection=test_insp.date_of_inspection,
        defaults={
            'client_name': test_insp.client_name,
            'internal_account_code': test_insp.internal_account_code,
            'inspector_name': test_insp.inspector_name,
            'product_name': test_insp.product_name,
            # km_traveled and hours NOT in defaults - should be preserved!
        }
    )

    # Check if preserved
    print(f"[AFTER]  km_traveled={inspection.km_traveled}, hours={inspection.hours}")

    if inspection.km_traveled == 999 and inspection.hours == 888:
        print(f"\n[SUCCESS] km/hours data PRESERVED by update_or_create!")
        print(f"   The fix is working correctly!")
    else:
        print(f"\n[FAILED] km/hours data NOT preserved!")
        print(f"   Expected: km=999, hours=888")
        print(f"   Got: km={inspection.km_traveled}, hours={inspection.hours}")

    # Clean up test data
    test_insp.km_traveled = None
    test_insp.hours = None
    test_insp.save()
    print(f"\n[CLEANUP] Reset test data to None")
else:
    print(f"\n[WARNING] No inspections found to test")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("\nNEXT STEPS:")
print("1. Add km/hours data to some inspections in the web interface")
print("2. Run a sync from the admin panel")
print("3. Verify that km/hours data is still there after sync!")
print("=" * 80)
