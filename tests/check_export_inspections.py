import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Q

# Get yesterday to today for default filter (same as export sheet)
today = datetime.now().date()
yesterday = today - timedelta(days=1)

print(f"Checking export sheet inspections from {yesterday} to {today}")
print("=" * 80)

# Apply the same filters as the export sheet
inspections = FoodSafetyAgencyInspection.objects.filter(
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=yesterday,
    date_of_inspection__lte=today
).filter(
    Q(fat=True) |
    Q(protein=True) |
    Q(calcium=True) |
    Q(dna=True) |
    Q(bought_sample__isnull=False)
).distinct('id').order_by('id', '-date_of_inspection', 'inspector_name')

print(f"\nTotal inspections that will be shown: {inspections.count()}\n")

if inspections.count() > 0:
    print("Inspections:")
    print("-" * 80)
    for insp in inspections:
        samples = []
        if insp.fat:
            samples.append("Fat")
        if insp.protein:
            samples.append("Protein")
        if insp.calcium:
            samples.append("Calcium")
        if insp.dna:
            samples.append("DNA")
        if insp.bought_sample:
            samples.append(f"Bought: {insp.bought_sample}")

        print(f"ID: {insp.id}")
        print(f"  Date: {insp.date_of_inspection}")
        print(f"  Inspector: {insp.inspector_name}")
        print(f"  Retailer: {insp.retailer_client_name}")
        print(f"  Hours: {insp.hours}, KM: {insp.km_traveled}")
        print(f"  Samples: {', '.join(samples) if samples else 'None'}")
        print(f"  Product Class: {insp.product_class}")
        print()
else:
    print("No inspections found matching the criteria.")
    print("\nLet's check inspections with hours and km but NO samples:")

    inspections_no_samples = FoodSafetyAgencyInspection.objects.filter(
        hours__isnull=False,
        km_traveled__isnull=False,
        date_of_inspection__gte=yesterday,
        date_of_inspection__lte=today
    ).exclude(
        Q(fat=True) |
        Q(protein=True) |
        Q(calcium=True) |
        Q(dna=True) |
        Q(bought_sample__isnull=False)
    ).distinct('id').order_by('id', '-date_of_inspection', 'inspector_name')

    print(f"\nInspections with hours/km but NO samples: {inspections_no_samples.count()}")
    if inspections_no_samples.count() > 0:
        print("-" * 80)
        for insp in inspections_no_samples[:10]:  # Show first 10
            print(f"ID: {insp.id}")
            print(f"  Date: {insp.date_of_inspection}")
            print(f"  Inspector: {insp.inspector_name}")
            print(f"  Retailer: {insp.retailer_client_name}")
            print(f"  Hours: {insp.hours}, KM: {insp.km_traveled}")
            print(f"  Product Class: {insp.product_class}")
            print(f"  Fat: {insp.fat}, Protein: {insp.protein}, Calcium: {insp.calcium}")
            print(f"  DNA: {insp.dna}, Bought Sample: {insp.bought_sample}")
            print()
