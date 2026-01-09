"""
Export clients without account codes to CSV
"""
import os
import django
import csv
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Client
from django.db.models import Q

# Get clients without account codes
clients_no_code = Client.objects.filter(
    Q(internal_account_code__isnull=True) |
    Q(internal_account_code='') |
    Q(internal_account_code='-')
).order_by('name')

# Create CSV file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'clients_without_account_codes_{timestamp}.csv'

with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)

    # Write header
    writer.writerow(['Client Name', 'Client ID', 'Account Code', 'Email', 'Created Date'])

    # Write data
    for client in clients_no_code:
        created = client.created_at.strftime("%Y-%m-%d %H:%M") if client.created_at else "Unknown"
        email = client.email or client.manual_email or "-"
        account_code = client.internal_account_code or "-"

        writer.writerow([
            client.name,
            client.client_id,
            account_code,
            email,
            created
        ])

print(f"[OK] Exported {clients_no_code.count()} clients to {filename}")

# Also print the list to console
print("\n" + "=" * 100)
print("CLIENTS WITHOUT ACCOUNT CODES")
print("=" * 100)
print(f"{'#':<4} {'Client Name':<50} {'Client ID':<15} {'Email':<30}")
print("=" * 100)

for idx, client in enumerate(clients_no_code, 1):
    email = client.email or client.manual_email or "-"
    print(f"{idx:<4} {client.name:<50} {client.client_id:<15} {email:<30}")

print("=" * 100)
print(f"Total: {clients_no_code.count()} clients")
