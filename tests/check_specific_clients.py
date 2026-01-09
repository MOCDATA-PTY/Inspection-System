import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import ClientAllocation

# Check some specific clients that should have corporate groups
test_clients = [
    "Pick 'n Pay - Kroonstad",
    "Boxer Superstore Protea Glen",
    "Shoprite Kenako Mall",
    "Checkers Northmead Square",
    "Food Lover's Market Comaro Crossing",
    "Spar Newtown"
]

print("Checking specific clients:")
print("=" * 60)

for name in test_clients:
    clients = ClientAllocation.objects.filter(eclick_name__icontains=name[:20])
    if clients.exists():
        client = clients.first()
        print(f"\nClient: {client.eclick_name}")
        print(f"  Corporate Group: '{client.corporate_group}'")
    else:
        print(f"\n'{name}' - NOT FOUND")

print("\n" + "=" * 60)
