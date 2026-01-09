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
        (['pick n pay franchise', 'pnp franchise'], 'Pick n Pay - Franchise'),
        (['pick n pay corporate', 'pnp corporate'], 'Pick n Pay - Corporate'),
        (['pick n pay', 'pnp', "pick'n pay", 'picknpay'], 'Pick n Pay - Corporate'),
        
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


print("=" * 60)
print("POPULATING CORPORATE GROUPS FOR ALL CLIENTS")
print("=" * 60)

# Get all clients with empty corporate groups
clients = ClientAllocation.objects.filter(
    corporate_group__isnull=True
) | ClientAllocation.objects.filter(
    corporate_group=""
) | ClientAllocation.objects.filter(
    corporate_group__icontains="Other"
)

clients = clients.distinct()
total_clients = clients.count()

print(f"\nClients needing corporate group assignment: {total_clients}")
print("\nProcessing...")

updated_count = 0
group_counts = {}

for i, client in enumerate(clients, 1):
    if i % 100 == 0:
        print(f"  Processed {i}/{total_clients}...")

    detected_group = detect_corporate_group(client.eclick_name)

    client.corporate_group = detected_group
    client.save()
    updated_count += 1

    group_counts[detected_group] = group_counts.get(detected_group, 0) + 1

print(f"\nCompleted!")
print(f"  - Clients updated: {updated_count}")
print(f"  - Clients remaining as 'Other': {total_clients - updated_count}")

print("\nDetected Corporate Groups:")
print("-" * 60)
for group, count in sorted(group_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {group}: {count} clients")

print("\n" + "=" * 60)
print("DONE! Refresh your page to see the updated dropdowns.")
print("=" * 60)
