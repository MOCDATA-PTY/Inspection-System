"""
Test compliance document download after datetime fix
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

def test_compliance_download():
    print("="*70)
    print("TESTING COMPLIANCE DOCUMENT DOWNLOAD (DATETIME FIX)")
    print("="*70 + "\n")

    # Get recent November inspections
    start_date = date(2025, 11, 1)
    end_date = date(2025, 11, 30)

    recent_inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=start_date,
        date_of_inspection__lte=end_date
    ).exclude(
        client_name__isnull=True
    ).order_by('-date_of_inspection')[:10]

    total = recent_inspections.count()
    print(f"Testing with {total} November inspections\n")

    if total == 0:
        print("No November inspections found!")
        return

    # Build client mapping
    client_map = {}
    for client in Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code=''):
        key = normalize_client_name(client.name or '')
        if key:
            client_map[key] = client.internal_account_code

    print(f"Loaded {len(client_map)} client mappings\n")

    # Load Drive files (this will use the NEW folder structure)
    print("Loading Drive files from 2025 folder...")
    print("Using NEW folder ID: 1pzot8MQ-m3u0f9-BWxpBO40QgLmeZhRP\n")

    # Create a mock request object for authentication
    class MockRequest:
        def __init__(self):
            self.session = {}

    mock_request = MockRequest()
    file_lookup = load_drive_files_real(mock_request, use_cache=False)

    print(f"Found {len(file_lookup)} files in Drive\n")
    print("="*70)
    print("TESTING DATETIME FIX")
    print("="*70 + "\n")

    found_count = 0
    no_account_count = 0
    not_found_count = 0
    error_count = 0

    for i, inspection in enumerate(recent_inspections, 1):
        print(f"\n[{i}/{total}] Inspection ID: {inspection.remote_id}")
        print(f"  Client: {inspection.client_name}")
        print(f"  Date: {inspection.date_of_inspection} (type: {type(inspection.date_of_inspection).__name__})")
        print(f"  Commodity: {inspection.commodity}")

        # Get account code
        client_key = normalize_client_name(inspection.client_name or '')
        account_code = client_map.get(client_key, '')

        if not account_code:
            print(f"  [SKIP] No account code found")
            no_account_count += 1
            continue

        print(f"  Account Code: {account_code}")

        # Try to find document - this is where the datetime error would occur
        try:
            doc_link = find_document_link_apps_script_replica(
                account_code,
                str(inspection.commodity).lower().strip(),
                inspection.date_of_inspection,
                file_lookup
            )

            if doc_link and doc_link != "Document Not Found":
                print(f"  [SUCCESS] Found document!")
                print(f"  Link: {doc_link[:80]}...")
                found_count += 1
            else:
                print(f"  [NOT FOUND] No matching document")
                not_found_count += 1

        except TypeError as e:
            if "unsupported operand type" in str(e):
                print(f"  [DATETIME ERROR] {str(e)}")
                print(f"  THIS SHOULD NOT HAPPEN - FIX FAILED!")
                error_count += 1
            else:
                print(f"  [ERROR] {str(e)}")
                error_count += 1
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            error_count += 1

    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    print(f"Total Tested: {total}")
    print(f"Documents Found: {found_count}")
    print(f"Not Found: {not_found_count}")
    print(f"No Account Code: {no_account_count}")
    print(f"Errors (including datetime): {error_count}")

    if error_count == 0:
        print("\n[SUCCESS] No datetime errors! The fix is working correctly.")
        if found_count > 0:
            print(f"[SUCCESS] Found {found_count} documents successfully.")
        print("\nThe compliance pull should now work without datetime errors.")
    else:
        print("\n[WARNING] Errors occurred during testing.")
        print("Check the output above for details.")

    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        test_compliance_download()
    except Exception as e:
        print(f"\n[FATAL ERROR] Test crashed: {e}")
        import traceback
        traceback.print_exc()
