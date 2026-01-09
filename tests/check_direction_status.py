#!/usr/bin/env python
"""
Check compliance status distribution in database
This helps verify if is_direction_present_for_this_inspection is being synced correctly
"""
import os
import sys
import django

# Set up Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Count

print("=" * 80)
print("COMPLIANCE STATUS CHECK (is_direction_present_for_this_inspection)")
print("=" * 80)

# Get total counts
total = FoodSafetyAgencyInspection.objects.count()
non_compliant = FoodSafetyAgencyInspection.objects.filter(is_direction_present_for_this_inspection=True).count()
compliant = FoodSafetyAgencyInspection.objects.filter(is_direction_present_for_this_inspection=False).count()

print(f"\nTotal inspections: {total}")
print(f"Compliant (no direction): {compliant}")
print(f"Non-Compliant (direction present): {non_compliant}")
print(f"Percentage non-compliant: {(non_compliant/total*100) if total > 0 else 0:.2f}%")

# Get breakdown by commodity
print("\n" + "-" * 40)
print("BREAKDOWN BY COMMODITY:")
print("-" * 40)

for commodity in ['POULTRY', 'EGGS', 'RAW', 'PMP']:
    total_c = FoodSafetyAgencyInspection.objects.filter(commodity=commodity).count()
    non_c = FoodSafetyAgencyInspection.objects.filter(
        commodity=commodity,
        is_direction_present_for_this_inspection=True
    ).count()
    print(f"{commodity}: {non_c}/{total_c} non-compliant")

# Find groups with mixed compliance
print("\n" + "-" * 40)
print("GROUPS WITH MIXED COMPLIANCE STATUS:")
print("-" * 40)

from django.db.models import Sum, Case, When, IntegerField

# Find client/date combinations with both compliant and non-compliant
groups = FoodSafetyAgencyInspection.objects.values(
    'client_name', 'date_of_inspection'
).annotate(
    total=Count('id'),
    non_compliant_count=Sum(
        Case(
            When(is_direction_present_for_this_inspection=True, then=1),
            default=0,
            output_field=IntegerField()
        )
    ),
    compliant_count=Sum(
        Case(
            When(is_direction_present_for_this_inspection=False, then=1),
            default=0,
            output_field=IntegerField()
        )
    )
).filter(
    non_compliant_count__gt=0,
    compliant_count__gt=0
).order_by('-date_of_inspection')[:10]

if groups:
    for g in groups:
        print(f"\n{g['client_name']} on {g['date_of_inspection']}:")
        print(f"  - Total inspections: {g['total']}")
        print(f"  - Compliant: {g['compliant_count']}")
        print(f"  - Non-compliant: {g['non_compliant_count']}")

        # Show individual inspections in this group
        inspections = FoodSafetyAgencyInspection.objects.filter(
            client_name=g['client_name'],
            date_of_inspection=g['date_of_inspection']
        ).values('remote_id', 'commodity', 'product_name', 'is_direction_present_for_this_inspection')

        for insp in inspections:
            status = "NON-COMPLIANT" if insp['is_direction_present_for_this_inspection'] else "Compliant"
            print(f"    - ID {insp['remote_id']} ({insp['commodity']}): {status} - {insp['product_name']}")
else:
    print("\nNo groups found with mixed compliance status.")
    print("This means either all inspections in each group are compliant,")
    print("or all inspections in each group are non-compliant.")

# Show some sample non-compliant inspections if any exist
print("\n" + "-" * 40)
print("SAMPLE NON-COMPLIANT INSPECTIONS:")
print("-" * 40)

non_compliant_samples = FoodSafetyAgencyInspection.objects.filter(
    is_direction_present_for_this_inspection=True
).order_by('-date_of_inspection')[:5]

if non_compliant_samples:
    for insp in non_compliant_samples:
        print(f"- ID {insp.remote_id}: {insp.client_name} ({insp.commodity}) on {insp.date_of_inspection}")
else:
    print("No non-compliant inspections found in database!")
    print("This likely means the is_direction_present_for_this_inspection field")
    print("is not being synced correctly from SQL Server.")

print("\n" + "=" * 80)
