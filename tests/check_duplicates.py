import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Count
from datetime import datetime, timedelta

# Check for duplicates
print("Checking for duplicate inspections...")
print("=" * 80)

# Get inspections with duplicates based on key fields
duplicates = FoodSafetyAgencyInspection.objects.values(
    'remote_id', 'date_of_inspection', 'inspector_name', 'client_name'
).annotate(
    count=Count('id')
).filter(count__gt=1).order_by('-count')

print(f"\nFound {len(duplicates)} sets of duplicate inspections")

if duplicates:
    print("\nTop 10 duplicate sets:")
    for dup in duplicates[:10]:
        print(f"\n  Remote ID: {dup['remote_id']}")
        print(f"  Date: {dup['date_of_inspection']}")
        print(f"  Inspector: {dup['inspector_name']}")
        print(f"  Client: {dup['client_name']}")
        print(f"  Count: {dup['count']} records")

        # Show the actual records
        records = FoodSafetyAgencyInspection.objects.filter(
            remote_id=dup['remote_id'],
            date_of_inspection=dup['date_of_inspection'],
            inspector_name=dup['inspector_name'],
            client_name=dup['client_name']
        )

        print(f"  IDs: {[r.id for r in records]}")

# Check for "Roots Butchery - Moons Ofsp" specifically
print("\n" + "=" * 80)
print("Checking 'Roots Butchery - Moons Ofsp' specifically:")
print("=" * 80)

roots_inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains='Roots Butchery - Moons'
).order_by('date_of_inspection')

print(f"\nFound {roots_inspections.count()} inspections")

for insp in roots_inspections[:20]:
    print(f"\nID: {insp.id}, Remote ID: {insp.remote_id}")
    print(f"  Date: {insp.date_of_inspection}")
    print(f"  Inspector: {insp.inspector_name}")
    print(f"  Client: {insp.client_name}")
    print(f"  Hours: {insp.hours}, KM: {insp.km_traveled}")
    print(f"  Commodity: {insp.commodity}")
