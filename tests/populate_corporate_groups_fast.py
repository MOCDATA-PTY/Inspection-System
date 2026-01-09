import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import ClientAllocation

def detect_corporate_group(client_name):
    """Auto-detect corporate group based on client name"""
    if not client_name:
        return "Other (Unlisted Group)"

    name = client_name.lower().strip()

    # Corporate group matching rules (ordered by specificity)
    rules = [
        # Pick n Pay variations
        (['pick n pay franchise', 'pnp franchise', "pick 'n pay franchise"], 'Pick n Pay - Franchise'),
        (['pick n pay corporate', 'pnp corporate', "pick 'n pay corporate"], 'Pick n Pay - Corporate'),
        (['pick n pay', 'pnp', "pick'n pay", "pick 'n pay", 'picknpay'], 'Pick n Pay - Corporate'),

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
        (['food lovers market', "food lover's market", 'foodlovers'], 'Food Lovers Market'),

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

        # Nesta Foods
        (['nesta foods', 'nesta'], 'Nesta Foods'),

        # Eskort
        (['eskort'], 'Eskort'),
    ]

    # Check each rule
    for keywords, group in rules:
        for keyword in keywords:
            if keyword in name:
                return group

    return "Other (Unlisted Group)"


print("=" * 60, flush=True)
print("POPULATING CORPORATE GROUPS (FAST VERSION)", flush=True)
print("=" * 60, flush=True)

# Get all clients with empty corporate groups
from django.db.models import Q
clients = ClientAllocation.objects.filter(
    Q(corporate_group__isnull=True) | Q(corporate_group="") | Q(corporate_group__icontains="Other")
)

total_clients = clients.count()
print(f"\nClients needing corporate group assignment: {total_clients}", flush=True)
print("\nProcessing in batches...", flush=True)

# Process in batches for efficiency
batch_size = 1000
group_counts = {}
updated_count = 0

for i in range(0, total_clients, batch_size):
    batch = list(clients[i:i+batch_size])

    # Update each client in the batch
    for client in batch:
        detected_group = detect_corporate_group(client.eclick_name)
        client.corporate_group = detected_group
        group_counts[detected_group] = group_counts.get(detected_group, 0) + 1

    # Bulk update the batch
    ClientAllocation.objects.bulk_update(batch, ['corporate_group'])
    updated_count += len(batch)
    print(f"  Processed {updated_count}/{total_clients}...", flush=True)

print(f"\nCompleted!", flush=True)
print(f"  - Total clients updated: {updated_count}", flush=True)

print("\nCorporate Groups Assigned:", flush=True)
print("-" * 60, flush=True)
for group, count in sorted(group_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {group}: {count} clients", flush=True)

print("\n" + "=" * 60, flush=True)
print("DONE! Refresh your page to see the updated corporate groups.", flush=True)
print("=" * 60, flush=True)
