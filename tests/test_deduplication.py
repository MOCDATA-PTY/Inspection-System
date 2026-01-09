import os
import sys
import django
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 100)
print("TESTING EXPORT DEDUPLICATION")
print("=" * 100)

# Test date range
start = datetime(2025, 12, 1).date()
end = datetime(2025, 12, 10).date()

print(f"\nTest period: {start} to {end}")
print("-" * 100)

# Fetch inspections (same query as export)
inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=start,
    date_of_inspection__lte=end
).order_by('client_name', 'date_of_inspection', 'commodity')

total_count = inspections.count()
print(f"\n1. Total inspections fetched from database: {total_count}")

# Apply deduplication (same logic as export)
seen_inspections = set()
unique_inspections = []
duplicate_count = 0

for inspection in inspections:
    unique_key = (
        inspection.inspector_name or '',
        inspection.client_name or '',
        inspection.commodity or '',
        str(inspection.date_of_inspection) if inspection.date_of_inspection else '',
        inspection.product_name or ''
    )

    if unique_key in seen_inspections:
        duplicate_count += 1
        print(f"\n   [DUPLICATE] {inspection.client_name} - {inspection.commodity} - {inspection.date_of_inspection} - {inspection.product_name}")
    else:
        seen_inspections.add(unique_key)
        unique_inspections.append(inspection)

print(f"\n2. After deduplication:")
print(f"   - Unique inspections: {len(unique_inspections)}")
print(f"   - Duplicates removed: {duplicate_count}")

# Check for specific known duplicates
print("\n" + "=" * 100)
print("CHECKING SPECIFIC CASES")
print("=" * 100)

# Check Mndeni Meats (should have 2 unique RAW, not 3)
mndeni = [i for i in unique_inspections if 'Mndeni Meats' in (i.client_name or '') and i.commodity == 'RAW']
print(f"\n3. Mndeni Meats RAW inspections (should be 2, not 3):")
print(f"   Found: {len(mndeni)}")
for idx, insp in enumerate(mndeni, 1):
    print(f"   {idx}. {insp.product_name} (ID: {insp.remote_id})")

# Check for any client with multiple identical inspections
print("\n4. Checking for clients with potential duplicates...")
client_commodity_date_products = {}
for insp in unique_inspections:
    key = (insp.client_name, insp.commodity, insp.date_of_inspection)
    if key not in client_commodity_date_products:
        client_commodity_date_products[key] = []
    client_commodity_date_products[key].append(insp.product_name)

duplicates_found = []
for key, products in client_commodity_date_products.items():
    # Check if there are duplicate product names
    if len(products) != len(set(products)):
        client, commodity, date = key
        duplicates_found.append((client, commodity, date, products))

if duplicates_found:
    print(f"\n   WARNING: Found {len(duplicates_found)} cases with duplicate products:")
    for client, commodity, date, products in duplicates_found[:5]:
        print(f"   - {client} / {commodity} / {date}: {products}")
else:
    print("\n   [OK] No duplicate products found!")

# Summary
print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"Total inspections in DB:     {total_count}")
print(f"Unique inspections:          {len(unique_inspections)}")
print(f"Duplicates removed:          {duplicate_count}")
print(f"Deduplication rate:          {(duplicate_count/total_count*100):.1f}%")

if duplicate_count == 0:
    print("\n[FAIL] No duplicates found - deduplication may not be working!")
elif duplicate_count < 10:
    print(f"\n[OK] Deduplication working - {duplicate_count} duplicates removed")
else:
    print(f"\n[WARNING] High number of duplicates ({duplicate_count}) - check data quality")

print("\n" + "=" * 100)
