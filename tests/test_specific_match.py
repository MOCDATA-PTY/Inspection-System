"""
Test specific inspection-to-file matching
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

def test_specific_match():
    # Get a specific inspection that should have a document
    inspection_id = 305178  # From the logs

    try:
        inspection = FoodSafetyAgencyInspection.objects.get(remote_id=inspection_id)
    except:
        print(f"Inspection {inspection_id} not found")
        return

    print("Inspection Details:")
    print("="*70)
    print(f"ID: {inspection.remote_id}")
    print(f"Client: {inspection.client_name}")
    print(f"Date: {inspection.date_of_inspection}")
    print(f"Commodity: '{inspection.commodity}'")
    print()

    # Get account code
    client_map = {}
    for client in Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code=''):
        key = normalize_client_name(client.name or '')
        if key:
            client_map[key] = client.internal_account_code

    client_key = normalize_client_name(inspection.client_name or '')
    account_code = client_map.get(client_key, '')

    print(f"Account Code: {account_code}")
    print()

    # Load files
    class MockRequest:
        def __init__(self):
            self.session = {}

    mock_request = MockRequest()
    file_lookup = load_drive_files_real(mock_request, use_cache=True)

    print(f"Total files in Drive: {len(file_lookup)}")
    print()

    # Show matching logic
    commodity_str = str(inspection.commodity).lower().strip()
    if commodity_str == "eggs":
        commodity_str = "egg"

    print(f"Normalized commodity for search: '{commodity_str}'")
    print(f"Looking for matches with: commodity='{commodity_str}' AND account_code='{account_code}'")
    print()

    # Find potential matches (same account code)
    account_matches = []
    for key, file_info in file_lookup.items():
        if file_info['accountCode'] == account_code:
            account_matches.append(file_info)

    print(f"Files with matching account code ({account_code}): {len(account_matches)}")
    if account_matches:
        for file_info in account_matches[:5]:
            print(f"  - {file_info['name']}")
            print(f"    Commodity: '{file_info['commodity']}' (lowercase: '{file_info['commodity'].lower()}')")
            print(f"    Date: {file_info['zipDateStr']}")
    print()

    # Try the actual match
    doc_link = find_document_link_apps_script_replica(
        account_code,
        str(inspection.commodity).lower().strip(),
        inspection.date_of_inspection,
        file_lookup
    )

    print("Match Result:")
    print("="*70)
    if doc_link and doc_link != "Document Not Found":
        print("FOUND!")
        print(doc_link)
    else:
        print("NOT FOUND")

if __name__ == "__main__":
    test_specific_match()
