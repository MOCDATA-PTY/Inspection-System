"""
Investigate inspections with directions being labeled incorrectly
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import datetime, timedelta

print("=" * 100)
print("INVESTIGATING DIRECTION/COMPLIANCE LABELING ISSUE")
print("=" * 100)

# Get recent inspections (last 30 days)
thirty_days_ago = datetime.now().date() - timedelta(days=30)
recent_inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=thirty_days_ago
).order_by('-date_of_inspection')

total = recent_inspections.count()
with_direction = recent_inspections.filter(is_direction_present_for_this_inspection=True).count()
without_direction = recent_inspections.filter(is_direction_present_for_this_inspection=False).count()

print(f"\nRecent Inspections (Last 30 Days):")
print(f"  Total: {total}")
print(f"  With Direction (Non-Compliant): {with_direction} ({with_direction/total*100:.1f}%)")
print(f"  Without Direction (Compliant): {without_direction} ({without_direction/total*100:.1f}%)")

# Show sample inspections with directions
print("\n" + "=" * 100)
print("SAMPLE INSPECTIONS WITH DIRECTION (Should be Non-Compliant)")
print("=" * 100)

inspections_with_direction = recent_inspections.filter(
    is_direction_present_for_this_inspection=True
)[:10]

if inspections_with_direction.exists():
    print(f"\n{'ID':<15} {'Date':<12} {'Client':<30} {'Direction':<10} {'Expected':<15}")
    print("-" * 100)
    for insp in inspections_with_direction:
        insp_id = insp.unique_inspection_id[:13]
        date = insp.date_of_inspection.strftime('%Y-%m-%d') if insp.date_of_inspection else 'N/A'
        client = (insp.client_name or 'Unknown')[:28]
        direction = 'YES' if insp.is_direction_present_for_this_inspection else 'NO'
        expected = 'Non-Compliant'
        print(f"{insp_id:<15} {date:<12} {client:<30} {direction:<10} {expected:<15}")
else:
    print("\nNo inspections with directions found in last 30 days")

# Show sample inspections without directions
print("\n" + "=" * 100)
print("SAMPLE INSPECTIONS WITHOUT DIRECTION (Should be Compliant)")
print("=" * 100)

inspections_without_direction = recent_inspections.filter(
    is_direction_present_for_this_inspection=False
)[:10]

if inspections_without_direction.exists():
    print(f"\n{'ID':<15} {'Date':<12} {'Client':<30} {'Direction':<10} {'Expected':<15}")
    print("-" * 100)
    for insp in inspections_without_direction:
        insp_id = insp.unique_inspection_id[:13]
        date = insp.date_of_inspection.strftime('%Y-%m-%d') if insp.date_of_inspection else 'N/A'
        client = (insp.client_name or 'Unknown')[:28]
        direction = 'YES' if insp.is_direction_present_for_this_inspection else 'NO'
        expected = 'Compliant'
        print(f"{insp_id:<15} {date:<12} {client:<30} {direction:<10} {expected:<15}")

# Check for NULL values
print("\n" + "=" * 100)
print("CHECKING FOR NULL/NONE VALUES")
print("=" * 100)

null_direction = FoodSafetyAgencyInspection.objects.filter(
    is_direction_present_for_this_inspection__isnull=True
).count()

print(f"\nInspections with NULL direction value: {null_direction}")

if null_direction > 0:
    print("\n[WARNING] Found inspections with NULL direction values!")
    print("These may be causing confusion in the UI")

# Summary
print("\n" + "=" * 100)
print("LOGIC EXPLANATION")
print("=" * 100)
print("""
CORRECT LOGIC:
- Direction Present = True  → Non-Compliant (business has issues to fix)
- Direction Present = False → Compliant (inspection passed)

A "Direction" in food safety means a formal notice of non-compliance.
If a direction is present, the business failed the inspection.

If you're seeing inspections WITH directions labeled as "Compliant",
please provide specific inspection IDs so I can investigate the display logic.
""")

print("=" * 100)
