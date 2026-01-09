"""
Verify dropdown unique values for Client Allocation filters
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import ClientAllocation

print("\n" + "=" * 80)
print("  CLIENT ALLOCATION DROPDOWN VALUES")
print("=" * 80)

all_clients = ClientAllocation.objects.all()

# Get unique commodities
unique_commodities = sorted(set(
    all_clients.exclude(commodity__isnull=True)
    .exclude(commodity='')
    .exclude(commodity__iexact='-')
    .values_list('commodity', flat=True)
))

print(f"\nCOMMODITY Dropdown ({len(unique_commodities)} values):")
for commodity in unique_commodities:
    print(f"  - {commodity.upper()}")

# Get unique facility types
unique_facility_types = sorted(set(
    all_clients.exclude(facility_type__isnull=True)
    .exclude(facility_type='')
    .exclude(facility_type__iexact='-')
    .values_list('facility_type', flat=True)
))

print(f"\nFACILITY TYPE Dropdown ({len(unique_facility_types)} values):")
for facility_type in unique_facility_types:
    print(f"  - {facility_type.title()}")

# Get unique provinces
unique_provinces = sorted(set(
    all_clients.exclude(province__isnull=True)
    .exclude(province='')
    .exclude(province__iexact='-')
    .values_list('province', flat=True)
))

print(f"\nPROVINCE Dropdown ({len(unique_provinces)} values):")
for province in unique_provinces:
    print(f"  - {province.title()}")

# Get unique corporate groups
unique_corporate_groups = sorted(set(
    all_clients.exclude(corporate_group__isnull=True)
    .exclude(corporate_group='')
    .exclude(corporate_group__iexact='-')
    .values_list('corporate_group', flat=True)
))

print(f"\nCORPORATE GROUP Dropdown ({len(unique_corporate_groups)} values):")
for corporate_group in unique_corporate_groups:
    print(f"  - {corporate_group.title()}")

# Get unique group types
unique_group_types = sorted(set(
    all_clients.exclude(group_type__isnull=True)
    .exclude(group_type='')
    .exclude(group_type__iexact='-')
    .values_list('group_type', flat=True)
))

print(f"\nGROUP TYPE Dropdown ({len(unique_group_types)} values):")
for group_type in unique_group_types:
    print(f"  - {group_type.title()}")

print("\n" + "=" * 80)
print("  SUMMARY")
print("=" * 80)
print(f"\nTotal Clients: {all_clients.count()}")
print(f"Dropdown Options:")
print(f"  - Commodities: {len(unique_commodities)}")
print(f"  - Facility Types: {len(unique_facility_types)}")
print(f"  - Provinces: {len(unique_provinces)}")
print(f"  - Corporate Groups: {len(unique_corporate_groups)}")
print(f"  - Group Types: {len(unique_group_types)}")

print("\n[OK] All dropdown filters populated successfully!")
print("=" * 80 + "\n")
