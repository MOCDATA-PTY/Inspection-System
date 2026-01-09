"""
Check which clients are missing account codes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Client
from django.db.models import Q

print("=" * 80)
print("CHECKING CLIENTS WITHOUT ACCOUNT CODES")
print("=" * 80)

# Get all clients
all_clients = Client.objects.all()
print(f"\nTotal clients in database: {all_clients.count()}")

# Get clients without account codes (NULL or empty string or '-')
clients_no_code = Client.objects.filter(
    Q(internal_account_code__isnull=True) |
    Q(internal_account_code='') |
    Q(internal_account_code='-')
)

print(f"Clients without account codes: {clients_no_code.count()}")

if clients_no_code.exists():
    print("\n" + "=" * 80)
    print("CLIENTS WITHOUT ACCOUNT CODES:")
    print("=" * 80)

    for client in clients_no_code.order_by('name'):
        created = client.created_at.strftime("%Y-%m-%d %H:%M") if client.created_at else "Unknown"
        email = client.email or client.manual_email or "No email"

        print(f"\nClient: {client.name}")
        print(f"  Client ID: {client.client_id}")
        print(f"  Account Code: {client.internal_account_code or 'NONE'}")
        print(f"  Email: {email}")
        print(f"  Created: {created}")

# Get clients with account codes for comparison
clients_with_code = Client.objects.exclude(
    Q(internal_account_code__isnull=True) |
    Q(internal_account_code='') |
    Q(internal_account_code='-')
)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total clients: {all_clients.count()}")
print(f"Clients WITH account codes: {clients_with_code.count()}")
print(f"Clients WITHOUT account codes: {clients_no_code.count()}")
if all_clients.count() > 0:
    print(f"Percentage missing: {(clients_no_code.count() / all_clients.count() * 100):.1f}%")

# Show some examples of clients WITH account codes
print("\n" + "=" * 80)
print("SAMPLE CLIENTS WITH ACCOUNT CODES (first 10):")
print("=" * 80)
for client in clients_with_code[:10]:
    print(f"  {client.name} -> {client.internal_account_code}")

print("\n" + "=" * 80)
