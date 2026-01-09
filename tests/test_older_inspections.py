"""
Test document matching for older November inspections
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, Client
from main.views.core_views import load_drive_files_real, find_document_link_apps_script_replica
from datetime import date

def normalize_client_name(name):
    """Normalize client name for matching"""
    if not name:
        return ''
    return name.strip().lower().replace(' ', '').replace('-', '').replace('_', '')

def test_older_inspections():
    print("="*70)
    print("TESTING DOCUMENT MATCHING FOR OLDER NOVEMBER INSPECTIONS")
    print("="*70 + "\n")

    # Get inspections from early November (should have documents by now)
    start_date = date(2025, 11, 1)
    end_date = date(2025, 11, 15)  # Mid-November

    older_inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=start_date,
        date_of_inspection__lte=end_date
    ).exclude(
        client_name__isnull=True
    ).order_by('-date_of_inspection')[:20]

    total = older_inspections.count()
    print(f"Testing with {total} inspections from Nov 1-15, 2025\n")

    if total == 0:
        print("No inspections found in early November!")
        return

    # Build client mapping
    client_map = {}
    for client in Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code=''):
        key = normalize_client_name(client.name or '')
        if key:
            client_map[key] = client.internal_account_code

    print(f"Loaded {len(client_map)} client mappings\n")

    # Load Drive files
    print("Loading Drive files...")
    class MockRequest:
        def __init__(self):
            self.session = {}

    mock_request = MockRequest()
    file_lookup = load_drive_files_real(mock_request, use_cache=True)

    print(f"Loaded {len(file_lookup)} files from Drive\n")

    # Show sample of available files
    print("Sample of available files in Drive:")
    for i, (key, file_info) in enumerate(list(file_lookup.items())[:5]):
        print(f"  {i+1}. {file_info['name']}")
        print(f"     Key: {key}")
    print()

    print("="*70)
    print("TESTING DOCUMENT MATCHING")
    print("="*70 + "\n")

    found_count = 0
    no_account_count = 0
    not_found_count = 0

    for i, inspection in enumerate(older_inspections, 1):
        print(f"[{i}/{total}] Inspection {inspection.remote_id}")
        print(f"  Client: {inspection.client_name}")
        print(f"  Date: {inspection.date_of_inspection}")
        print(f"  Commodity: {inspection.commodity}")

        # Get account code
        client_key = normalize_client_name(inspection.client_name or '')
        account_code = client_map.get(client_key, '')

        if not account_code:
            print(f"  ❌ No account code\n")
            no_account_count += 1
            continue

        print(f"  Account: {account_code}")

        # Try to find document
        doc_link = find_document_link_apps_script_replica(
            account_code,
            str(inspection.commodity).lower().strip(),
            inspection.date_of_inspection,
            file_lookup
        )

        if doc_link and doc_link != "Document Not Found":
            print(f"  ✅ FOUND: {doc_link[:80]}...\n")
            found_count += 1
        else:
            print(f"  ❌ NOT FOUND\n")
            not_found_count += 1

    print("="*70)
    print("RESULTS")
    print("="*70)
    print(f"Total: {total}")
    print(f"Found: {found_count}")
    print(f"Not Found: {not_found_count}")
    print(f"No Account Code: {no_account_count}")
    print(f"\nSuccess Rate: {(found_count/total*100):.1f}%")

if __name__ == "__main__":
    test_older_inspections()
