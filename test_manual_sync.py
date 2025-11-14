"""
Test script to manually run SQL Server sync and verify product names are stored
"""

import os
import sys
import io
import django
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.scheduled_sync_service import scheduled_sync_service

print("=" * 80)
print("MANUAL SYNC TEST - FETCHING INSPECTIONS AND PRODUCT NAMES")
print("=" * 80)

print("\nStep 1: Running SQL Server sync...")
print("-" * 80)

success = scheduled_sync_service.sync_sql_server()

if success:
    print("\n\n" + "=" * 80)
    print("STEP 2: CHECKING PRODUCT NAMES IN DATABASE")
    print("=" * 80)

    from main.models import FoodSafetyAgencyInspection

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

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    percentage = (with_product_name / total * 100) if total > 0 else 0
    print(f"Product name coverage: {with_product_name}/{total} ({percentage:.1f}%)")

    if with_product_name == 0:
        print("\nWARNING: NO product names in database!")
        print("   The sync process is NOT storing product names.")
    elif with_product_name < total:
        print(f"\nPARTIAL: {total - with_product_name} inspections missing product names")
        print("   Some inspections may not have product data in SQL Server.")
    else:
        print("\nSUCCESS: All inspections have product names!")
else:
    print("\nERROR: Sync failed!")
