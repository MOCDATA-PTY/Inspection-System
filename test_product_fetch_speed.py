"""
Test how long it takes to fetch product names from SQL Server
"""

import os
import sys
import django
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from main.utils.sql_server_utils import fetch_product_names_for_inspection
from datetime import date

print("=" * 80)
print("TESTING SQL SERVER PRODUCT NAME FETCHING SPEED")
print("=" * 80)

# Get some recent inspections with remote_id
inspections = FoodSafetyAgencyInspection.objects.filter(
    remote_id__isnull=False
).order_by('-date_of_inspection')[:20]

print(f"\nTesting product name fetch for {inspections.count()} inspections...")

total_time = 0
successful = 0
failed = 0

for inspection in inspections:
    start = time.time()
    try:
        products = fetch_product_names_for_inspection(inspection_id=inspection.remote_id)
        elapsed = time.time() - start
        total_time += elapsed
        successful += 1
        print(f"  {inspection.remote_id}: {len(products)} products in {elapsed:.3f}s")
    except Exception as e:
        failed += 1
        print(f"  {inspection.remote_id}: FAILED - {e}")

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)
print(f"Total inspections tested: {inspections.count()}")
print(f"Successful: {successful}")
print(f"Failed: {failed}")
print(f"Total time: {total_time:.2f}s")
print(f"Average per inspection: {total_time/successful:.3f}s" if successful > 0 else "N/A")

# Estimate for ALL inspections
all_with_remote = FoodSafetyAgencyInspection.objects.filter(remote_id__isnull=False).count()
if successful > 0:
    estimated_total = (total_time/successful) * all_with_remote
    print(f"\nESTIMATED time for ALL {all_with_remote} inspections: {estimated_total:.2f}s ({estimated_total/60:.1f} minutes)")

    if estimated_total > 120:
        print("\n⚠️  WARNING: Product fetching would take over 2 minutes!")
        print("   This is likely causing the 504 timeout!")
        print("\n   SOLUTION: Cache product names in database instead of fetching every time")
