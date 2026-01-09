"""
Test with older November inspections that should have documents
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

def test():
    print("Testing with EARLY November inspections (Nov 1-10)\n")

    # Test with EARLY November - should have files by now
    start_date = date(2025, 11, 1)
    end_date = date(2025, 11, 10)

    inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=start_date,
        date_of_inspection__lte=end_date
    ).exclude(client_name__isnull=True).order_by('date_of_inspection')[:10]

    print(f"Found {inspections.count()} inspections from Nov 1-10\n")

    # Client mapping
    client_map = {}
    for client in Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code=''):
        key = normalize_client_name(client.name or '')
        if key:
            client_map[key] = client.internal_account_code

    # Load files
    class MockRequest:
        def __init__(self):
            self.session = {}

    file_lookup = load_drive_files_real(MockRequest(), use_cache=True)
    print(f"Loaded {len(file_lookup)} files\n")

    found = 0
    for i, inspection in enumerate(inspections, 1):
        client_key = normalize_client_name(inspection.client_name or '')
        account_code = client_map.get(client_key, '')

        if not account_code:
            continue

        doc_link = find_document_link_apps_script_replica(
            account_code,
            str(inspection.commodity).lower().strip(),
            inspection.date_of_inspection,
            file_lookup
        )

        status = "FOUND" if doc_link and doc_link != "Document Not Found" else "NOT FOUND"
        if status == "FOUND":
            found += 1

        print(f"[{i}] {inspection.date_of_inspection} | {inspection.client_name} | {status}")

    print(f"\nResult: {found}/{inspections.count()} found")

if __name__ == "__main__":
    test()
