"""
Auto-assign corporate groups based on client names
This script analyzes client names and automatically assigns appropriate corporate groups
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import ClientAllocation

# Corporate group mapping rules
# Format: (keywords to match in client name, corporate group to assign)
CORPORATE_GROUP_RULES = [
    # Pick n Pay variations
    (['pick n pay franchise', 'pnp franchise'], 'Pick n Pay - Franchise'),
    (['pick n pay corporate', 'pnp corporate'], 'Pick n Pay - Corporate'),
    (['pick n pay', 'pnp', 'pick\'n pay', 'picknpay'], 'Pick n Pay - Corporate'),

    # Fruit & Veg
    (['fruit & veg', 'fruit and veg', 'fruit&veg'], 'Fruit & Veg'),

    # OK Foods
    (['ok foods', 'ok food', 'okfoods'], 'OK Foods'),

    # Checkers
    (['checkers'], 'Checkers'),

    # Spar variations
    (['spar northrand', 'spar - northrand'], 'Spar - Northrand'),
    (['superspar', 'super spar'], 'SuperSpar'),
    (['spar'], 'Spar'),

    # Shoprite
    (['shoprite', 'shop rite'], 'Shoprite'),

    # Massmart
    (['massmart'], 'Massmart'),

    # Chester Butcheries
    (['chester butcheries', 'chester butchery'], 'Chester Butcheries'),

    # Boxer
    (['boxer'], 'Boxer'),

    # Food Lovers Market
    (['food lovers market', 'food lover\'s market', 'foodlovers'], 'Food Lovers Market'),

    # Cambridge
    (['cambridge'], 'Cambridge'),

    # Woolworths
    (['woolworths', 'woolworth'], 'Woolworths'),

    # Jwayelani
    (['jwayelani'], 'Jwayelani'),

    # Usave
    (['usave', 'u-save', 'u save'], 'Usave'),

    # OBC
    (['obc'], 'OBC'),

    # Roots
    (['roots'], 'Roots'),

    # Meat World
    (['meat world', 'meatworld'], 'Meat World'),

    # Quantum Foods Nulaid
    (['quantum foods', 'nulaid', 'quantum'], 'Quantum Foods Nulaid'),

    # Bluff Meat Supply
    (['bluff meat supply', 'bluff meat'], 'Bluff Meat Supply'),

    # Eat Sum Meat
    (['eat sum meat', 'eatsum'], 'Eat Sum Meat'),

    # Waltloo Meat and Chicken
    (['waltloo meat', 'waltloo chicken', 'waltloo'], 'Waltloo Meat and Chicken'),

    # Choppies
    (['choppies', 'choppy'], 'Choppies'),

    # Econo Foods
    (['econo foods', 'econofoods'], 'Econo Foods'),

    # Makro
    (['makro'], 'Makro'),

    # Boma Vleismark
    (['boma vleismark', 'boma vleis'], 'Boma Vleismark'),

    # Eskort
    (['eskort'], 'Eskort'),

    # Nesta Foods
    (['nesta foods', 'nesta'], 'Nesta Foods'),
]

def match_corporate_group(client_name):
    """
    Match a client name to a corporate group based on keywords
    Returns the corporate group name or "Other (Unlisted Group)" if no match
    """
    if not client_name:
        return "Other (Unlisted Group)"

    client_name_lower = client_name.lower().strip()

    # Check each rule in order (more specific rules first)
    for keywords, corporate_group in CORPORATE_GROUP_RULES:
        for keyword in keywords:
            if keyword.lower() in client_name_lower:
                return corporate_group

    return "Other (Unlisted Group)"

def analyze_clients(dry_run=True):
    """
    Analyze all clients and suggest corporate group assignments

    Args:
        dry_run: If True, only show suggestions. If False, actually update the database.
    """
    print("Analyzing Client Corporate Groups")
    print("=" * 80)

    clients = ClientAllocation.objects.all()
    total_clients = clients.count()

    print(f"\nTotal clients: {total_clients}")
    print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE UPDATE (will modify database)'}")
    print("\n" + "=" * 80)

    matched_count = 0
    updated_count = 0
    already_set_count = 0
    no_match_count = 0

    changes = []

    for client in clients:
        suggested_group = match_corporate_group(client.eclick_name)
        current_group = client.corporate_group

        # Count matches (excluding "Other (Unlisted Group)")
        if suggested_group != "Other (Unlisted Group)":
            matched_count += 1
        else:
            no_match_count += 1

        if current_group and current_group != '-' and current_group.strip():
            # Already has a corporate group
            if current_group != suggested_group:
                changes.append({
                    'id': client.id,
                    'client_id': client.client_id,
                    'name': client.eclick_name,
                    'current': current_group,
                    'suggested': suggested_group,
                    'action': 'CHANGE'
                })
            else:
                already_set_count += 1
        else:
            # No corporate group set, suggest one
            changes.append({
                'id': client.id,
                'client_id': client.client_id,
                'name': client.eclick_name,
                'current': current_group or '(none)',
                'suggested': suggested_group,
                'action': 'NEW'
            })

    # Show changes
    if changes:
        print(f"\n{'CLIENT ID':<12} {'CLIENT NAME':<40} {'CURRENT GROUP':<30} {'SUGGESTED GROUP':<30} {'ACTION':<10}")
        print("-" * 130)

        for change in changes[:50]:  # Show first 50
            print(f"{change['client_id']:<12} {change['name'][:38]:<40} {change['current'][:28]:<30} {change['suggested'][:28]:<30} {change['action']:<10}")

        if len(changes) > 50:
            print(f"\n... and {len(changes) - 50} more changes")

    print("\n" + "=" * 80)
    print(f"\nSummary:")
    print(f"  Total clients analyzed: {total_clients}")
    print(f"  Matched to corporate group: {matched_count}")
    print(f"  Already correctly set: {already_set_count}")
    print(f"  No match found: {no_match_count}")
    print(f"  Suggested changes: {len(changes)}")

    # Apply changes if not dry run
    if not dry_run and changes:
        print(f"\nApplying {len(changes)} changes...")

        for change in changes:
            client = ClientAllocation.objects.get(id=change['id'])
            client.corporate_group = change['suggested']
            client.save()
            updated_count += 1

        print(f"✓ Updated {updated_count} clients")
    elif dry_run and changes:
        print("\nTo apply these changes, run:")
        print("  python auto_assign_corporate_groups.py --apply")

    print("=" * 80)

def show_unmatched_clients():
    """Show clients that don't match any corporate group"""
    print("\nClients Without Corporate Group Match")
    print("=" * 80)

    clients = ClientAllocation.objects.all()
    unmatched = []

    for client in clients:
        if not match_corporate_group(client.eclick_name):
            current_group = client.corporate_group
            if not current_group or current_group == '-':
                unmatched.append({
                    'client_id': client.client_id,
                    'name': client.eclick_name,
                    'commodity': client.commodity or '-',
                })

    if unmatched:
        print(f"\n{'CLIENT ID':<12} {'CLIENT NAME':<50} {'COMMODITY':<20}")
        print("-" * 85)

        for client in unmatched[:100]:  # Show first 100
            print(f"{client['client_id']:<12} {client['name'][:48]:<50} {client['commodity'][:18]:<20}")

        if len(unmatched) > 100:
            print(f"\n... and {len(unmatched) - 100} more unmatched clients")

        print(f"\nTotal unmatched: {len(unmatched)}")
    else:
        print("\nAll clients are matched!")

    print("=" * 80)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Auto-assign corporate groups based on client names')
    parser.add_argument('--apply', action='store_true', help='Apply changes to database (default is dry run)')
    parser.add_argument('--unmatched', action='store_true', help='Show clients without matches')

    args = parser.parse_args()

    if args.unmatched:
        show_unmatched_clients()
    else:
        analyze_clients(dry_run=not args.apply)
