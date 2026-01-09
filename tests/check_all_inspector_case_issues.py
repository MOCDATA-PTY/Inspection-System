"""Check if other inspectors have case-sensitivity issues"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, InspectorMapping
from django.db.models import Q

print("=" * 80)
print("CHECKING FOR CASE-SENSITIVITY ISSUES IN ALL INSPECTOR MAPPINGS")
print("=" * 80)

# Get all active inspector mappings
mappings = InspectorMapping.objects.filter(is_active=True)
print(f"\nTotal active inspector mappings: {mappings.count()}")

issues_found = []

for mapping in mappings:
    inspector_id = mapping.inspector_id
    inspector_name = mapping.inspector_name

    # Check case-sensitive match
    case_sensitive = FoodSafetyAgencyInspection.objects.filter(
        Q(inspector_id=inspector_id) | Q(inspector_name=inspector_name)
    ).count()

    # Check case-insensitive match
    case_insensitive = FoodSafetyAgencyInspection.objects.filter(
        Q(inspector_id=inspector_id) | Q(inspector_name__iexact=inspector_name)
    ).count()

    # If counts differ, there's a case-sensitivity issue
    if case_sensitive != case_insensitive:
        issues_found.append({
            'name': inspector_name,
            'id': inspector_id,
            'case_sensitive': case_sensitive,
            'case_insensitive': case_insensitive,
            'missing': case_insensitive - case_sensitive
        })

        # Get the actual inspector names in database
        actual_names = FoodSafetyAgencyInspection.objects.filter(
            inspector_name__iexact=inspector_name
        ).values_list('inspector_name', flat=True).distinct()

print("\n" + "=" * 80)
print("INSPECTORS WITH CASE-SENSITIVITY ISSUES:")
print("=" * 80)

if issues_found:
    for issue in issues_found:
        print(f"\n{issue['name']} (ID: {issue['id']}):")
        print(f"  Case-sensitive match: {issue['case_sensitive']} inspections")
        print(f"  Case-insensitive match: {issue['case_insensitive']} inspections")
        print(f"  Missing due to case: {issue['missing']} inspections")
else:
    print("\nNo case-sensitivity issues found!")

print("\n" + "=" * 80)
print(f"TOTAL INSPECTORS WITH ISSUES: {len(issues_found)}")
print("=" * 80)
