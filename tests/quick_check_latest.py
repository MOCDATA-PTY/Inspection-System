"""
Quick check for latest inspections - run this after sync completes
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 80)
print("LATEST INSPECTIONS IN DATABASE")
print("=" * 80)
print()

# Total count
total = FoodSafetyAgencyInspection.objects.count()
print(f"Total inspections: {total}")
print()

# Latest 20 by date
print("Latest 20 inspections by date:")
print("-" * 80)

latest = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection', '-created_at')[:20]

for i, insp in enumerate(latest, 1):
    print(f"{i:2d}. {insp.date_of_inspection} | {insp.unique_inspection_id:15s} | {insp.inspector_name:20s} | {insp.client_name}")

print()
print("=" * 80)
