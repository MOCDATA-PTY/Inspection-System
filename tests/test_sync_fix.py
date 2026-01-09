"""
Test that the sync fix ACTUALLY WORKS
Verifies Boxer Superstore Sibasa inspections have correct products from correct tables
"""
import os
import sys
import django

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from main.services.scheduled_sync_service import ScheduledSyncService
from django.core.cache import cache

print("=" * 100)
print("TESTING SYNC FIX - VERIFY PRODUCTS ARE CORRECT")
print("=" * 100)

# Clear cache to prevent background service interference
cache.delete('scheduled_sync_service:running')
cache.delete('scheduled_sync_service:heartbeat')

# Clear existing data
print("\n1. CLEARING DATABASE...")
old_count = FoodSafetyAgencyInspection.objects.count()
FoodSafetyAgencyInspection.objects.all().delete()
print(f"   Deleted {old_count:,} old records")

# Run sync with fixed code
print("\n2. RUNNING SYNC WITH FIXED CODE...")
print("=" * 100)
service = ScheduledSyncService()
success = service.sync_sql_server()

if not success:
    print("\n❌ SYNC FAILED!")
    sys.exit(1)

print("\n" + "=" * 100)
print("3. CHECKING RESULTS")
print("=" * 100)

total = FoodSafetyAgencyInspection.objects.count()
print(f"\nTotal inspections: {total:,}")

if 3500 <= total <= 4500:
    print(f"✅ COUNT IS CORRECT! (Expected ~3,700-4,000)")
else:
    print(f"❌ COUNT IS WRONG! Expected ~3,700-4,000, got {total:,}")

# Check Boxer Superstore Sibasa inspections
print("\n" + "=" * 100)
print("4. CHECKING BOXER SUPERSTORE SIBASA - 03/12/2025")
print("=" * 100)

boxer_inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name='Boxer Superstore Sibasa',
    date_of_inspection__date='2025-12-03'
).order_by('commodity', 'remote_id')

print(f"\nFound {boxer_inspections.count()} inspections for Boxer Superstore Sibasa on 03/12/2025")

for insp in boxer_inspections:
    print(f"\n{'=' * 80}")
    print(f"Inspection ID: {insp.remote_id}")
    print(f"Commodity: {insp.commodity}")
    print(f"Product Name: '{insp.product_name}'")
    print(f"{'=' * 80}")

print("\n" + "=" * 100)
print("5. VERIFICATION")
print("=" * 100)

# Expected results based on test_boxer_inspections.py
expected = {
    '6596': {
        'commodity': 'POULTRY_LABEL',
        'product': 'Fresh Chicken Whole',  # Should NOT have "Dhanya wors" or "game Biltong"
    },
    '6597': {
        'commodity': 'POULTRY_LABEL',
        'product': 'Fresh Chicken Gizzards',  # Should NOT have "Boxer Boerewors" or "Cooked Salami"
    },
    '17125': {
        'commodity': 'EGGS',
        'product': '',  # Empty in SQL Server
    },
    '8684': {
        'commodity': 'PMP',
        'product': 'Crumbed Chicken Schnitzels',
    },
}

all_correct = True

for remote_id, expected_data in expected.items():
    insp = FoodSafetyAgencyInspection.objects.filter(
        remote_id=remote_id,
        commodity=expected_data['commodity']
    ).first()

    if not insp:
        print(f"\n❌ Inspection {remote_id} ({expected_data['commodity']}) NOT FOUND!")
        all_correct = False
        continue

    # Check product name (strip whitespace for comparison)
    actual_product = (insp.product_name or '').strip()
    expected_product = expected_data['product'].strip()

    if actual_product == expected_product:
        print(f"\n✅ Inspection {remote_id} ({expected_data['commodity']}): CORRECT")
        print(f"   Product: '{actual_product}'")
    else:
        print(f"\n❌ Inspection {remote_id} ({expected_data['commodity']}): WRONG!")
        print(f"   Expected: '{expected_product}'")
        print(f"   Got: '{actual_product}'")
        all_correct = False

    # Check for cross-contamination (products from wrong tables)
    if expected_data['commodity'] == 'POULTRY_LABEL':
        # Should NOT have products from PMP or RAW tables
        wrong_products = ['Dhanya wors', 'game Biltong', 'Boxer Boerewors', 'Cooked Salami']
        for wrong_prod in wrong_products:
            if wrong_prod.lower() in actual_product.lower():
                print(f"   ❌ CONTAMINATION! Found '{wrong_prod}' (from wrong table)")
                all_correct = False

print("\n" + "=" * 100)
print("FINAL RESULT")
print("=" * 100)

if all_correct and 3500 <= total <= 4500:
    print("\n✅✅✅ ALL TESTS PASSED! FIX IS WORKING! ✅✅✅")
    print("\n   - Count is correct (~3.7k)")
    print("   - Products are from correct tables only")
    print("   - No cross-contamination")
    print("\n🎉 READY TO DEPLOY!")
else:
    print("\n❌❌❌ TESTS FAILED! FIX IS NOT WORKING! ❌❌❌")

print("\n" + "=" * 100)
