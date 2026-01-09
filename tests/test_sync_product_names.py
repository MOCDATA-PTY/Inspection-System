"""
Test if sync stores product names in PostgreSQL database
"""

import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 80)
print("CHECKING PRODUCT NAMES IN POSTGRESQL DATABASE")
print("=" * 80)

# Check total inspections
total = FoodSafetyAgencyInspection.objects.count()
print(f"\nTotal inspections: {total}")

# Check how many have product names
with_product_name = FoodSafetyAgencyInspection.objects.exclude(
    product_name__isnull=True
).exclude(product_name='').count()

print(f"Inspections WITH product_name: {with_product_name}")
print(f"Inspections WITHOUT product_name: {total - with_product_name}")

# Show some examples
print("\n" + "=" * 80)
print("SAMPLE INSPECTIONS WITH PRODUCT NAMES")
print("=" * 80)

inspections_with_names = FoodSafetyAgencyInspection.objects.exclude(
    product_name__isnull=True
).exclude(product_name='')[:10]

if inspections_with_names:
    for insp in inspections_with_names:
        print(f"  ID: {insp.remote_id}, Client: {insp.client_name}, Product: {insp.product_name}")
else:
    print("  NO INSPECTIONS WITH PRODUCT NAMES FOUND!")

print("\n" + "=" * 80)
print("SAMPLE INSPECTIONS WITHOUT PRODUCT NAMES")
print("=" * 80)

inspections_without_names = FoodSafetyAgencyInspection.objects.filter(
    product_name__isnull=True
) | FoodSafetyAgencyInspection.objects.filter(product_name='')

inspections_without_names = inspections_without_names[:10]

if inspections_without_names:
    for insp in inspections_without_names:
        print(f"  ID: {insp.remote_id}, Client: {insp.client_name}, Product: {insp.product_name}")
else:
    print("  ALL INSPECTIONS HAVE PRODUCT NAMES!")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

percentage = (with_product_name / total * 100) if total > 0 else 0
print(f"Product name coverage: {with_product_name}/{total} ({percentage:.1f}%)")

if with_product_name == 0:
    print("\n⚠️  WARNING: NO product names in database!")
    print("   The sync process is NOT storing product names.")
    print("   Need to update sync to fetch and save product names from SQL Server.")
elif with_product_name < total:
    print(f"\n⚠️  PARTIAL: {total - with_product_name} inspections missing product names")
    print("   Sync may need to be run again to fill in missing data.")
else:
    print("\n✓ SUCCESS: All inspections have product names!")
