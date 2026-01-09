"""Test export sheet to check for duplicates locally"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import datetime, timedelta
from collections import defaultdict

print("=" * 100)
print("TESTING EXPORT SHEET LOGIC FOR DUPLICATES")
print("=" * 100)

# Test with yesterday to today
today = datetime.now().date()
yesterday = today - timedelta(days=1)

print(f"\nDate range: {yesterday} to {today}")

# Fetch inspections (same as export_sheet)
inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=yesterday,
    date_of_inspection__lte=today
).order_by('client_name', 'date_of_inspection', 'commodity')

print(f"Found {len(inspections)} inspections with hours/km")

# Group by visit (same logic as export)
visits = defaultdict(list)

for inspection in inspections:
    visit_key = (
        inspection.inspector_name or '',
        inspection.client_name or '',
        str(inspection.date_of_inspection) if inspection.date_of_inspection else ''
    )
    visits[visit_key].append(inspection)

print(f"\nGrouped into {len(visits)} unique visits")

# Check for duplicates
print("\n" + "=" * 100)
print("CHECKING FOR DUPLICATE ISSUES:")
print("=" * 100)

issues_found = False

for visit_key, visit_inspections in visits.items():
    inspector_name, client_name, date_str = visit_key

    if len(visit_inspections) > 1:
        print(f"\n[VISIT] {client_name} - {date_str} - {inspector_name}")
        print(f"  Products inspected: {len(visit_inspections)}")

        # Check if all have same hours/km
        hours_values = [float(i.hours) if i.hours else 0 for i in visit_inspections]
        km_values = [float(i.km_traveled) if i.km_traveled else 0 for i in visit_inspections]

        unique_hours = set(hours_values)
        unique_km = set(km_values)

        if len(unique_hours) > 1 or len(unique_km) > 1:
            print(f"  [WARNING] Different hours/km values in same visit!")
            print(f"    Hours: {hours_values}")
            print(f"    KM: {km_values}")
            issues_found = True
        else:
            print(f"  Hours/KM consistent: {hours_values[0]}hrs, {km_values[0]}km")

        # Show products
        for i, insp in enumerate(visit_inspections, 1):
            print(f"  Product {i}: {insp.commodity} - {insp.product_name}")
            print(f"    Fat: {insp.fat}, Protein: {insp.protein}, Sample taken: {insp.is_sample_taken}")

print("\n" + "=" * 100)
if issues_found:
    print("ISSUES FOUND - Review warnings above")
else:
    print("NO ISSUES FOUND - All visits have consistent hours/km")
print("=" * 100)
