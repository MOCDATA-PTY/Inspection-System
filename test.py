#!/usr/bin/env python
"""Test account code loading in shipment list view."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Client, FoodSafetyAgencyInspection, User, InspectorMapping
from django.db.models import Q
from datetime import datetime, timedelta
import re

print("=" * 80)
print("TESTING ACCOUNT CODE LOADING")
print("=" * 80)

# Get inspector user (like Nelisa from the screenshot)
inspector = User.objects.filter(username='Nelisa').first()
if not inspector:
    inspector = User.objects.filter(role='inspector').first()

print(f"\n[1] Testing with user: {inspector.username}")

# Get inspector mapping
try:
    mapping = InspectorMapping.objects.get(
        inspector_name=inspector.get_full_name() or inspector.username
    )
    inspector_id = mapping.inspector_id
    inspector_name = mapping.inspector_name
    print(f"    Inspector ID: {inspector_id}, Name: {inspector_name}")
except InspectorMapping.DoesNotExist:
    print(f"    ERROR: No mapping found!")
    exit(1)

# Get inspections (last 60 days)
sixty_days_ago = (datetime.now() - timedelta(days=60)).date()
inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=sixty_days_ago
)

# Filter by inspector
inspections = inspections.filter(
    Q(inspector_id=inspector_id) | Q(inspector_name=inspector_name)
)

print(f"\n[2] Found {inspections.count()} inspections for this inspector")

# Group inspections (like the view does)
from django.db.models import Count, Max, Min
groups = inspections.values('client_name', 'date_of_inspection').annotate(
    inspection_count=Count('id'),
    latest_inspection_id=Max('id'),
    earliest_inspection_id=Min('id'),
).order_by('-date_of_inspection', 'client_name')[:25]

client_date_groups = list(groups)
print(f"\n[3] Grouped into {len(client_date_groups)} groups")

# Extract client names (like the optimization does)
client_names_on_page = set(group['client_name'] for group in client_date_groups if group.get('client_name'))
print(f"\n[4] Unique client names on page: {len(client_names_on_page)}")

# Build query like the code does
print(f"\n[5] Building client query...")
client_query = Q()
for client_name in client_names_on_page:
    if client_name:
        client_query |= Q(client_id__iexact=client_name) | Q(name__iexact=client_name)

if client_query:
    clients_queryset = Client.objects.filter(client_query)
else:
    clients_queryset = Client.objects.none()

print(f"    Query will search for {len(client_names_on_page)} client names")
print(f"    Found {clients_queryset.count()} clients in database")

# Test normalization function
def _norm(text):
    try:
        cleaned = re.sub(r'[\(\)\[\]{}\\/._,-]', ' ', (text or ''))
        cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()
        return cleaned
    except Exception:
        return (text or '').strip().lower()

# Build the client map like the code does
print(f"\n[6] Building client maps...")
_client_map = {}
_client_id_map = {}

for _c in clients_queryset:
    key_id = _norm(_c.client_id)
    key_name = _norm(_c.name)

    if key_id:
        if _c.internal_account_code:
            _client_map[key_id] = _c.internal_account_code
        _client_id_map[key_id] = _c.client_id

    # Also map by name as fallback
    if key_name and key_name != key_id:
        if _c.internal_account_code and key_name not in _client_map:
            _client_map[key_name] = _c.internal_account_code
        if key_name not in _client_id_map:
            _client_id_map[key_name] = _c.client_id

print(f"    Client map has {len(_client_map)} entries")
print(f"    Client ID map has {len(_client_id_map)} entries")

# Test getting account codes for each group
print(f"\n[7] Testing account code retrieval for each group:")
print("=" * 80)

def _get_internal_account_code(raw_name):
    """Get internal account code from cache ONLY - NO database queries for performance"""
    try:
        # Use normalized key for lookup in pre-built cache
        code = _client_map.get(_norm(raw_name))
        if code:
            return code
    except Exception:
        pass
    return None

for i, group in enumerate(client_date_groups[:10], 1):  # Test first 10
    client_name = group['client_name']
    account_code = _get_internal_account_code(client_name) if client_name else None

    print(f"\n{i}. Client: {client_name}")
    print(f"   Normalized: {_norm(client_name)}")
    print(f"   Account Code: {account_code or '[MISSING]'}")

    # Debug: check if key exists
    norm_name = _norm(client_name)
    if norm_name in _client_map:
        print(f"   [OK] Key '{norm_name}' found in _client_map")
    else:
        print(f"   [ERROR] Key '{norm_name}' NOT in _client_map")
        print(f"   Available keys starting with same letter: {[k for k in _client_map.keys() if k and k[0] == norm_name[0]][:3]}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total groups: {len(client_date_groups)}")
print(f"Clients in database: {clients_queryset.count()}")
print(f"Client map entries: {len(_client_map)}")
print(f"Missing account codes: {sum(1 for g in client_date_groups if not _get_internal_account_code(g['client_name']))}")

# Show if there's a mismatch
if clients_queryset.count() != len(client_names_on_page):
    print(f"\n[WARNING] Expected {len(client_names_on_page)} clients but found {clients_queryset.count()}")
    print("Missing clients:")
    found_names = set(_norm(c.client_id) for c in clients_queryset) | set(_norm(c.name) for c in clients_queryset)
    for name in client_names_on_page:
        norm = _norm(name)
        if norm not in found_names:
            print(f"  - {name} (normalized: {norm})")
