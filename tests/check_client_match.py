#!/usr/bin/env python
"""Check why client names aren't matching"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Client
from django.db.models import Q

# Test names from the debug output
test_names = [
    "Food Lover's Market - Knysna",
    "Frederik Van Heerden",
    "Boxer Superstore - Kwanokuthula"
]

print("=" * 80)
print("TESTING CLIENT NAME MATCHING")
print("=" * 80)

for name in test_names:
    print(f"\nSearching for: '{name}'")

    # Try exact match (what the current code does)
    exact_match = Client.objects.filter(Q(client_id__in=[name]) | Q(name__in=[name]))
    print(f"  Exact match (__in): {exact_match.count()} clients")

    # Try contains match
    contains_match = Client.objects.filter(Q(client_id__icontains=name) | Q(name__icontains=name))
    print(f"  Contains match (__icontains): {contains_match.count()} clients")

    if contains_match.exists():
        for c in contains_match[:3]:
            print(f"    - client_id='{c.client_id}' name='{c.name}' code='{c.internal_account_code}'")
