"""
Debug why export sheet isn't showing data
"""
import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Q

print("="*80)
print("DEBUGGING EXPORT SHEET")
print("="*80)

# This is the exact query from export_sheet view
inspections = FoodSafetyAgencyInspection.objects.filter(
    Q(hours__isnull=False) |
    Q(km_traveled__isnull=False) |
    Q(fat=True) |
    Q(protein=True) |
    Q(calcium=True) |
    Q(dna=True) |
    Q(bought_sample__isnull=False)
).order_by('-date_of_inspection', 'inspector_name')

total_count = inspections.count()
print(f"\nTotal inspections with billable data: {total_count}")

# Check Oct-Nov specifically
oct_nov = inspections.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date()
)

oct_nov_count = oct_nov.count()
print(f"Oct-Nov 2025 inspections: {oct_nov_count}")

# Sample some inspections
print("\n" + "-"*80)
print("SAMPLE INSPECTIONS (first 10):")
print("-"*80)

for insp in oct_nov[:10]:
    print(f"\nDate: {insp.date_of_inspection}")
    print(f"  Client: {insp.client_name}")
    print(f"  Inspector ID: {insp.inspector_id}")
    print(f"  Inspector Name: {insp.inspector_name}")  # THIS IS THE KEY FIELD
    print(f"  Hours: {insp.hours}")
    print(f"  KM: {insp.km_traveled}")
    print(f"  Commodity: {insp.commodity}")
    print(f"  Product Name: {insp.product_name}")

# Check inspector_name NULLs
null_inspector_name = oct_nov.filter(inspector_name__isnull=True).count()
empty_inspector_name = oct_nov.filter(inspector_name='').count()
print("\n" + "-"*80)
print("INSPECTOR NAME ANALYSIS:")
print("-"*80)
print(f"Inspections with NULL inspector_name: {null_inspector_name}")
print(f"Inspections with empty inspector_name: {empty_inspector_name}")
print(f"Inspections with populated inspector_name: {oct_nov_count - null_inspector_name - empty_inspector_name}")

# Check inspector_id to name mapping
print("\n" + "-"*80)
print("INSPECTOR ID TO NAME MAPPING:")
print("-"*80)

from django.contrib.auth.models import User

inspector_ids = oct_nov.values_list('inspector_id', flat=True).distinct()
for insp_id in inspector_ids:
    if insp_id:
        try:
            user = User.objects.get(id=insp_id)
            count = oct_nov.filter(inspector_id=insp_id).count()
            print(f"  ID {insp_id}: {user.first_name} {user.last_name} (username: {user.username}) - {count} inspections")
        except User.DoesNotExist:
            count = oct_nov.filter(inspector_id=insp_id).count()
            print(f"  ID {insp_id}: USER NOT FOUND - {count} inspections")
    else:
        count = oct_nov.filter(inspector_id__isnull=True).count()
        print(f"  NULL: {count} inspections")

print("\n" + "="*80)
print("Done!")
