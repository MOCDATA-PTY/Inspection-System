"""
Test script to analyze what's making the inspections page slow
"""

import os
import sys
import django
import time
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import date

print("=" * 80)
print("PERFORMANCE ANALYSIS")
print("=" * 80)

# Check how many inspections we're loading
print("\n1. COUNTING INSPECTIONS")
print("-" * 80)

total_inspections = FoodSafetyAgencyInspection.objects.count()
recent_inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=date(2025, 10, 1)
).count()

print(f"Total inspections in database: {total_inspections}")
print(f"Recent inspections (Oct 2025+): {recent_inspections}")

# Test how long it takes to load inspections
print("\n2. TIMING INSPECTION QUERY")
print("-" * 80)

start = time.time()
inspections = list(FoodSafetyAgencyInspection.objects.all()[:100])
query_time = time.time() - start

print(f"Time to load 100 inspections: {query_time:.2f} seconds")

# Group by client and date (like the actual page does)
print("\n3. GROUPING INSPECTIONS")
print("-" * 80)

start = time.time()
from itertools import groupby
from operator import attrgetter

inspections = FoodSafetyAgencyInspection.objects.all()[:100]
grouped = {}
for key, group in groupby(inspections, key=lambda x: (x.client_name, x.date_of_inspection)):
    client_name, inspection_date = key
    grouped[f"{client_name} - {inspection_date}"] = list(group)

grouping_time = time.time() - start

print(f"Number of groups: {len(grouped)}")
print(f"Time to group: {grouping_time:.2f} seconds")

# Test compliance checking
print("\n4. TESTING COMPLIANCE CHECK SPEED")
print("-" * 80)

import re
from django.conf import settings

def quick_compliance_check(client_name, inspection_date):
    """Simplified compliance check"""
    date_obj = inspection_date if hasattr(inspection_date, 'strftime') else date.fromisoformat(str(inspection_date))
    year_folder = date_obj.strftime('%Y')
    month_folder = date_obj.strftime('%B')

    compliance_path = os.path.join(
        settings.MEDIA_ROOT,
        'inspection',
        year_folder,
        month_folder,
        client_name,
        'Compliance'
    )

    return os.path.exists(compliance_path)

# Test compliance check speed
test_groups = list(grouped.items())[:10]
start = time.time()
for group_name, group_inspections in test_groups:
    client_name = group_inspections[0].client_name
    inspection_date = group_inspections[0].date_of_inspection
    quick_compliance_check(client_name, inspection_date)

compliance_time = time.time() - start

print(f"Time to check 10 groups: {compliance_time:.2f} seconds")
print(f"Average per group: {compliance_time/10:.2f} seconds")

# Summary
print("\n" + "=" * 80)
print("PERFORMANCE SUMMARY")
print("=" * 80)
print(f"Total inspections: {total_inspections}")
print(f"Groups created: {len(grouped)}")
print(f"Query time: {query_time:.2f}s")
print(f"Grouping time: {grouping_time:.2f}s")
print(f"Compliance check (per group): {compliance_time/10:.2f}s")
print(f"Estimated total for {len(grouped)} groups: {(compliance_time/10) * len(grouped):.2f}s")
print("=" * 80)

print("\nPROBLEM IDENTIFIED:")
if (compliance_time/10) * len(grouped) > 60:
    print("  -> Compliance checking is TOO SLOW for many groups!")
    print("  -> Need to cache compliance results or defer to AJAX")
else:
    print("  -> Something else is causing the slowdown")
