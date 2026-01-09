"""
Find the actual latest inspections including December 29 and beyond
"""
import os
import django
import sys
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Max, Count, Q

def main():
    print("=" * 80)
    print("FINDING ACTUAL LATEST INSPECTIONS")
    print("=" * 80)
    print()

    # Get the absolute latest by created_at
    print("1. Latest by CREATED_AT (when added to database):")
    print("-" * 80)
    latest_created = FoodSafetyAgencyInspection.objects.order_by('-created_at').first()
    if latest_created:
        print(f"ID: {latest_created.id}")
        print(f"Unique ID: {latest_created.unique_inspection_id}")
        print(f"Inspector: {latest_created.inspector_name}")
        print(f"Client: {latest_created.client_name}")
        print(f"Inspection Date: {latest_created.date_of_inspection}")
        print(f"Created At: {latest_created.created_at}")
        print(f"Updated At: {latest_created.updated_at}")
    print()

    # Get the latest by inspection date
    print("2. Latest by INSPECTION_DATE (when inspection happened):")
    print("-" * 80)
    latest_inspection = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection').first()
    if latest_inspection:
        print(f"ID: {latest_inspection.id}")
        print(f"Unique ID: {latest_inspection.unique_inspection_id}")
        print(f"Inspector: {latest_inspection.inspector_name}")
        print(f"Client: {latest_inspection.client_name}")
        print(f"Inspection Date: {latest_inspection.date_of_inspection}")
        print(f"Created At: {latest_inspection.created_at}")
    print()

    # Show all inspections from December 2025
    print("3. ALL December 2025 Inspections (by date):")
    print("-" * 80)
    december_inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__year=2025,
        date_of_inspection__month=12
    ).order_by('-date_of_inspection', '-created_at')

    print(f"Total December 2025 inspections: {december_inspections.count()}")
    print()

    # Group by date
    print("Breakdown by date:")
    date_counts = december_inspections.values('date_of_inspection').annotate(
        count=Count('id')
    ).order_by('-date_of_inspection')

    for item in date_counts[:15]:  # Show top 15 dates
        print(f"  {item['date_of_inspection']}: {item['count']} inspections")
    print()

    # Show top 10 most recent inspections
    print("4. Top 10 Most Recent Inspections (by inspection date):")
    print("-" * 80)
    recent = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection', '-created_at')[:10]

    for i, insp in enumerate(recent, 1):
        print(f"{i}. [{insp.unique_inspection_id}] {insp.inspector_name} - {insp.client_name}")
        print(f"   Inspection Date: {insp.date_of_inspection} | Created: {insp.created_at.strftime('%Y-%m-%d %H:%M')}")
        print()

    # Check for inspections after Dec 24
    print("5. Inspections AFTER December 24, 2025:")
    print("-" * 80)
    after_dec24 = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gt='2025-12-24'
    ).order_by('-date_of_inspection', '-created_at')[:20]

    print(f"Total inspections after Dec 24: {after_dec24.count()}")
    if after_dec24.count() > 0:
        print("\nFirst 20:")
        for i, insp in enumerate(after_dec24, 1):
            print(f"{i}. [{insp.unique_inspection_id}] {insp.date_of_inspection} - {insp.inspector_name} - {insp.client_name}")
    print()

    # Check specifically for Dec 29, 30, 31
    print("6. Specific Date Check (Dec 29, 30, 31, 2025):")
    print("-" * 80)
    for day in [29, 30, 31]:
        count = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection__year=2025,
            date_of_inspection__month=12,
            date_of_inspection__day=day
        ).count()
        print(f"Dec {day}, 2025: {count} inspections")
    print()

    # Check for 2026 inspections
    print("7. Check for 2026 Inspections:")
    print("-" * 80)
    jan_2026 = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__year=2026,
        date_of_inspection__month=1
    ).order_by('-date_of_inspection')[:10]

    print(f"Total January 2026 inspections: {jan_2026.count()}")
    if jan_2026.count() > 0:
        print("\nFirst 10:")
        for i, insp in enumerate(jan_2026, 1):
            print(f"{i}. [{insp.unique_inspection_id}] {insp.date_of_inspection} - {insp.inspector_name} - {insp.client_name}")
    print()

    print("=" * 80)
    print("INVESTIGATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
