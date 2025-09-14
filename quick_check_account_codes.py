#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection as Insp, Client
from django.db.models import Q

# Pick a few distinct client names from inspections
client_names = list(
    Insp.objects.values_list('client_name', flat=True).distinct()[:10]
)

print("Checking internal_account_code mapping for sample inspection client names:\n")
for name in client_names:
    client = (
        Client.objects.filter(Q(client_id__iexact=name) | Q(name__iexact=name))
        .only('client_id', 'name', 'internal_account_code')
        .first()
    )
    print(f"Inspection client_name: '{name}'")
    if client:
        print(f" -> Client match: client_id='{client.client_id}', name='{client.name}', internal_account_code='{client.internal_account_code}'")
    else:
        print(" -> No Client row found matching client_id or name (case-insensitive)")
    print("")

# Also summarize how many Clients have internal_account_code set
total = Client.objects.count()
with_code = Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code__exact='').count()
print(f"Clients with internal_account_code set: {with_code}/{total}")

