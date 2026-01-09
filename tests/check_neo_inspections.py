"""Check NEO's inspections in the database"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import datetime, timedelta

print("=" * 80)
print("CHECKING NEO'S INSPECTIONS IN DATABASE")
print("=" * 80)

# Total inspections
total = FoodSafetyAgencyInspection.objects.count()
print(f"\nTotal inspections in database: {total}")

# Check by inspector_id=118
print("\n" + "=" * 80)
print("Inspections with inspector_id=118:")
print("=" * 80)
neo_by_id = FoodSafetyAgencyInspection.objects.filter(inspector_id=118)
print(f"Count: {neo_by_id.count()}")
if neo_by_id.exists():
    print("\nSample inspections:")
    for insp in neo_by_id[:5]:
        print(f"  - ID: {insp.remote_id}, Client: {insp.client_name}, Date: {insp.date_of_inspection}")

# Check by inspector_name
print("\n" + "=" * 80)
print("Inspections with inspector_name containing 'neo':")
print("=" * 80)
neo_by_name = FoodSafetyAgencyInspection.objects.filter(inspector_name__icontains='neo')
print(f"Count: {neo_by_name.count()}")
if neo_by_name.exists():
    unique_names = neo_by_name.values_list('inspector_name', flat=True).distinct()
    print(f"Unique inspector names: {list(unique_names)}")
    print("\nSample inspections:")
    for insp in neo_by_name[:5]:
        print(f"  - ID: {insp.remote_id}, Inspector: {insp.inspector_name}, Client: {insp.client_name}, Date: {insp.date_of_inspection}")

# Check in last 60 days
print("\n" + "=" * 80)
print("Inspections in last 60 days:")
print("=" * 80)
sixty_days_ago = (datetime.now() - timedelta(days=60)).date()
print(f"60 days ago: {sixty_days_ago}")
recent = FoodSafetyAgencyInspection.objects.filter(date_of_inspection__gte=sixty_days_ago)
print(f"Total recent inspections: {recent.count()}")

neo_recent_id = recent.filter(inspector_id=118)
print(f"Recent inspections for inspector_id=118: {neo_recent_id.count()}")

neo_recent_name = recent.filter(inspector_name__icontains='neo')
print(f"Recent inspections for inspector_name containing 'neo': {neo_recent_name.count()}")

# Check with exact name match "Neo Noe"
print("\n" + "=" * 80)
print("Inspections with exact inspector_name='Neo Noe' or 'NEO NOE':")
print("=" * 80)
neo_exact = FoodSafetyAgencyInspection.objects.filter(inspector_name__iexact='Neo Noe')
print(f"Count (case insensitive 'Neo Noe'): {neo_exact.count()}")

neo_exact2 = FoodSafetyAgencyInspection.objects.filter(inspector_name__iexact='NEO NOE')
print(f"Count (case insensitive 'NEO NOE'): {neo_exact2.count()}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Inspector ID 118 (all time): {neo_by_id.count()}")
print(f"Inspector name 'neo' (all time): {neo_by_name.count()}")
print(f"Inspector ID 118 (last 60 days): {neo_recent_id.count()}")
print(f"Inspector name 'neo' (last 60 days): {neo_recent_name.count()}")
