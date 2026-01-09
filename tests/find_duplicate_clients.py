"""
Find duplicate clients with "New Producer /", "New Retailer /", etc. prefixes
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Client

print('\n' + '='*80)
print(' FINDING DUPLICATE CLIENTS WITH PREFIXES')
print('='*80)

# Find all clients with "New" prefix patterns
prefixes = [
    'New Producer /',
    'New Retailer /',
    'New Manufacturer /',
    'New Distributor /',
    'New Wholesaler /',
    'New /',
]

duplicates_found = []

for prefix in prefixes:
    clients_with_prefix = Client.objects.filter(name__startswith=prefix)

    for client in clients_with_prefix:
        # Extract the actual name after the prefix
        actual_name = client.name.replace(prefix, '').strip()

        # Look for a client with just that name (without prefix)
        matching_client = Client.objects.filter(name=actual_name).first()

        if matching_client:
            duplicates_found.append({
                'prefix_version': client,
                'original': matching_client,
                'actual_name': actual_name,
                'prefix': prefix
            })

print(f'\nFound {len(duplicates_found)} duplicate pairs:\n')

if duplicates_found:
    for i, dup in enumerate(duplicates_found, 1):
        print(f'{i}. Duplicate Pair:')
        print(f'   Prefixed: "{dup["prefix_version"].name}" (ID: {dup["prefix_version"].id})')
        print(f'   Original: "{dup["original"].name}" (ID: {dup["original"].id})')
        print(f'   Account Code (Prefixed): {dup["prefix_version"].account_code}')
        print(f'   Account Code (Original): {dup["original"].account_code}')
        print(f'   Prefix Used: {dup["prefix"]}')
        print()

    # Also search for any clients starting with "New" that might not match the patterns
    print('\n' + '-'*80)
    print(' ALL CLIENTS STARTING WITH "New"')
    print('-'*80)

    all_new_clients = Client.objects.filter(name__startswith='New').order_by('name')
    print(f'\nTotal clients starting with "New": {all_new_clients.count()}\n')

    for client in all_new_clients[:50]:  # Show first 50
        print(f'  - "{client.name}" (ID: {client.id}, Account: {client.account_code})')

else:
    print('No duplicates found with the standard prefixes.')
    print('\nSearching for any clients with "New" in the name...')

    new_clients = Client.objects.filter(name__icontains='New').order_by('name')
    print(f'Found {new_clients.count()} clients with "New" in their name\n')

    for client in new_clients[:30]:
        print(f'  - "{client.name}" (ID: {client.id})')

print('\n' + '='*80 + '\n')
