import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import ClientAllocation

print("=" * 60)
print("TESTING CORPORATE GROUPS GENERATION")
print("=" * 60)

# Get all clients
all_clients = ClientAllocation.objects.all()
print(f"\nTotal clients in database: {all_clients.count()}")

# Get all corporate groups (including None/empty)
all_corporate_groups = all_clients.values_list('corporate_group', flat=True)
print(f"\nTotal corporate group entries: {len(all_corporate_groups)}")

# Count None/empty values
none_count = sum(1 for g in all_corporate_groups if not g)
print(f"  - Empty/None corporate groups: {none_count}")
print(f"  - Non-empty corporate groups: {len(all_corporate_groups) - none_count}")

# Get unique corporate groups (excluding None/empty)
unique_corporate_groups = sorted(set(
    group for group in all_corporate_groups
    if group and group.strip()
))

print(f"\nUnique corporate groups (sorted): {len(unique_corporate_groups)}")
print("\nCorporate Groups List:")
print("-" * 60)
if unique_corporate_groups:
    for i, group in enumerate(unique_corporate_groups, 1):
        print(f"{i:3}. {group}")
else:
    print("WARNING: NO CORPORATE GROUPS FOUND!")
    print("\nShowing first 10 clients to debug:")
    for client in all_clients[:10]:
        print(f"  - {client.eclick_name}: '{client.corporate_group}'")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
