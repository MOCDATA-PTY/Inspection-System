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

# Check last 30 days
today = datetime.now().date()
start_date = today - timedelta(days=30)

print(f"Checking export sheet inspections from {start_date} to {today}")
print("=" * 80)

# Apply the same filters as the export sheet
inspections = FoodSafetyAgencyInspection.objects.filter(
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=start_date,
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
    print(f"Showing first 20 inspections:")
    print("-" * 80)
    for insp in inspections[:20]:
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

        print(f"ID: {insp.id} | Date: {insp.date_of_inspection} | Inspector: {insp.inspector_name}")
        print(f"  Client: {insp.client_name}")
        print(f"  Hours: {insp.hours}, KM: {insp.km_traveled}")
        print(f"  Samples: {', '.join(samples)}")
        print(f"  Product Class: {insp.product_class}")
        print()
else:
    print("No inspections found matching the criteria.")

print("\n" + "=" * 80)
print("Checking inspections with hours/km but NO samples (would be filtered out):")
print("=" * 80)

inspections_no_samples = FoodSafetyAgencyInspection.objects.filter(
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=start_date,
    date_of_inspection__lte=today
).exclude(
    Q(fat=True) |
    Q(protein=True) |
    Q(calcium=True) |
    Q(dna=True) |
    Q(bought_sample__isnull=False)
).distinct('id').order_by('id', '-date_of_inspection', 'inspector_name')

print(f"\nInspections with hours/km but NO samples (filtered out): {inspections_no_samples.count()}")
if inspections_no_samples.count() > 0:
    print(f"\nShowing first 10 filtered out inspections:")
    print("-" * 80)
    for insp in inspections_no_samples[:10]:
        print(f"ID: {insp.id} | Date: {insp.date_of_inspection} | Inspector: {insp.inspector_name}")
        print(f"  Client: {insp.client_name}")
        print(f"  Hours: {insp.hours}, KM: {insp.km_traveled}")
        print(f"  Product Class: {insp.product_class}")
        print(f"  Fat: {insp.fat}, Protein: {insp.protein}, Calcium: {insp.calcium}")
        print(f"  DNA: {insp.dna}, Bought Sample: {insp.bought_sample}")
        print()

print("\n" + "=" * 80)
print("Summary:")
print("=" * 80)
print(f"[SHOWN] Inspections that WILL be shown: {inspections.count()}")
print(f"[FILTERED] Inspections that will be FILTERED OUT: {inspections_no_samples.count()}")
print(f"Total with hours/km: {inspections.count() + inspections_no_samples.count()}")

# Check if ANY inspections in the entire database have sample data
print("\n" + "=" * 80)
print("Checking if ANY inspections have sample data in the entire database:")
print("=" * 80)

all_with_samples = FoodSafetyAgencyInspection.objects.filter(
    Q(fat=True) |
    Q(protein=True) |
    Q(calcium=True) |
    Q(dna=True) |
    Q(bought_sample__isnull=False)
).count()

print(f"\nInspections with ANY sample data: {all_with_samples}")

if all_with_samples > 0:
    print("\nSample data:")
    sample_inspections = FoodSafetyAgencyInspection.objects.filter(
        Q(fat=True) |
        Q(protein=True) |
        Q(calcium=True) |
        Q(dna=True) |
        Q(bought_sample__isnull=False)
    ).order_by('-date_of_inspection')[:5]

    for insp in sample_inspections:
        print(f"ID: {insp.id} | Date: {insp.date_of_inspection}")
        print(f"  Fat: {insp.fat}, Protein: {insp.protein}, Calcium: {insp.calcium}")
        print(f"  DNA: {insp.dna}, Bought Sample: {insp.bought_sample}")
        print()
