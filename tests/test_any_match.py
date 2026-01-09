"""
Test matching for ANY recent November inspection
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, Client
from main.views.core_views import load_drive_files_real, find_document_link_apps_script_replica
from datetime import date

def normalize_client_name(name):
    if not name:
        return ''
    return name.strip().lower().replace(' ', '').replace('-', '').replace('_', '')

def test_any_match():
    # Get a recent November inspection with account code
    start_date = date(2025, 11, 1)
    end_date = date(2025, 11, 15)

    # Build client map first
    client_map = {}
    for client in Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code=''):
        key = normalize_client_name(client.name or '')
        if key:
            client_map[key] = client.internal_account_code

    print(f"Loaded {len(client_map)} clients")

    # Find an inspection with account code
    inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=start_date,
        date_of_inspection__lte=end_date
    ).exclude(client_name__isnull=True).order_by('date_of_inspection')[:50]

    print(f"Checking {inspections.count()} inspections...\n")

    # Load files
    class MockRequest:
        def __init__(self):
            self.session = {}

    mock_request = MockRequest()
    file_lookup = load_drive_files_real(mock_request, use_cache=True)

    print(f"Total files in Drive: {len(file_lookup)}\n")

    # Test first few with account codes
    tested = 0
    for inspection in inspections:
        client_key = normalize_client_name(inspection.client_name or '')
        account_code = client_map.get(client_key, '')

        if not account_code:
            continue

        tested += 1

        print("="*70)
        print(f"Inspection #{tested}")
        print(f"ID: {inspection.remote_id}")
        print(f"Client: {inspection.client_name}")
        print(f"Date: {inspection.date_of_inspection}")
        print(f"Commodity: '{inspection.commodity}'")
        print(f"Account: {account_code}")

        # Find files with same account code
        account_files = []
        for key, file_info in file_lookup.items():
            if file_info['accountCode'] == account_code:
                account_files.append(file_info)

        print(f"\nFiles for this account: {len(account_files)}")

        if account_files:
            print("\nAvailable files:")
            for file_info in account_files[:3]:
                print(f"  - {file_info['name']}")
                print(f"    Commodity: '{file_info['commodity']}' (lower: '{file_info['commodity'].lower()}')")
                print(f"    Date: {file_info['zipDateStr']}")

        # Normalize commodity
        commodity_str = str(inspection.commodity).lower().strip()
        if commodity_str == "eggs":
            commodity_str = "egg"

        print(f"\nSearch commodity: '{commodity_str}'")

        # Try match
        doc_link = find_document_link_apps_script_replica(
            account_code,
            str(inspection.commodity).lower().strip(),
            inspection.date_of_inspection,
            file_lookup
        )

        if doc_link and doc_link != "Document Not Found":
            print("Result: FOUND!")
        else:
            print("Result: NOT FOUND")

        if tested >= 5:
            break

if __name__ == "__main__":
    test_any_match()
