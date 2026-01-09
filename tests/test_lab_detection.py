import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Inspection, Client
from datetime import datetime
import json

def test_lab_file_detection():
    """Test lab file detection for various clients"""

    print("\n" + "="*80)
    print("LAB FILE DETECTION TEST")
    print("="*80 + "\n")

    # Get recent inspections - ALL of them
    inspections = Inspection.objects.filter(
        inspection_date__gte='2025-11-01'
    ).order_by('-inspection_date')[:100]

    print(f"Testing {len(inspections)} recent inspections...\n")

    has_files_count = 0
    no_files_count = 0

    for inspection in inspections:
        client_name = inspection.facility_client_name if inspection.facility_client_name else 'Unknown'
        date_str = inspection.inspection_date.strftime('%Y-%m-%d')

        # Clean client name for folder path
        cleaned_name = client_name.lower()
        cleaned_name = cleaned_name.replace(' - ', '_')
        cleaned_name = cleaned_name.replace('-', '_')
        cleaned_name = cleaned_name.replace(' ', '_')
        cleaned_name = cleaned_name.replace('/', '_')
        cleaned_name = cleaned_name.replace('&', 'and')
        cleaned_name = cleaned_name.replace("'", '')
        cleaned_name = cleaned_name.replace('"', '')
        cleaned_name = cleaned_name.replace('.', '')

        # Build expected folder path
        year = inspection.inspection_date.strftime('%Y')
        month = inspection.inspection_date.strftime('%B')

        base_path = f'/root/Inspection-System/media/inspection/{year}/{month}'

        # Check multiple folder variations
        folder_variations = [
            cleaned_name,
            f"mobile_{cleaned_name}"
        ]

        all_files = []
        found_folder = None
        actual_folder_name = None

        for folder_var in folder_variations:
            folder_path = os.path.join(base_path, folder_var)

            if os.path.exists(folder_path):
                found_folder = folder_path
                actual_folder_name = folder_var

                # Check for Compliance folder
                compliance_path = os.path.join(folder_path, 'Compliance')
                if os.path.exists(compliance_path):
                    # Check all commodity subfolders
                    for commodity in os.listdir(compliance_path):
                        commodity_path = os.path.join(compliance_path, commodity)
                        if os.path.isdir(commodity_path):
                            for filename in os.listdir(commodity_path):
                                if os.path.isfile(os.path.join(commodity_path, filename)):
                                    filename_lower = filename.lower()
                                    # Categorize file type
                                    file_type = 'other'
                                    if 'lab' in filename_lower or filename_lower.startswith('fsl-') or filename_lower.startswith('lab-'):
                                        file_type = 'lab'
                                    elif 'rfi' in filename_lower or filename_lower.startswith('fsa-rfi'):
                                        file_type = 'rfi'
                                    elif 'inv' in filename_lower or 'invoice' in filename_lower or filename_lower.startswith('fsa-inv'):
                                        file_type = 'invoice'

                                    all_files.append({
                                        'file': filename,
                                        'type': file_type,
                                        'commodity': commodity,
                                        'path': os.path.join(commodity_path, filename)
                                    })

                # Check for RFI folder
                rfi_path = os.path.join(folder_path, 'rfi')
                if os.path.exists(rfi_path):
                    for filename in os.listdir(rfi_path):
                        if os.path.isfile(os.path.join(rfi_path, filename)):
                            all_files.append({
                                'file': filename,
                                'type': 'rfi',
                                'folder': 'rfi',
                                'path': os.path.join(rfi_path, filename)
                            })

        if all_files:
            has_files_count += 1
            # Count by type
            lab_files = [f for f in all_files if f['type'] == 'lab']
            rfi_files = [f for f in all_files if f['type'] == 'rfi']
            invoice_files = [f for f in all_files if f['type'] == 'invoice']

            print(f"✓ [{inspection.id}] {client_name} ({date_str}) - Commodity: {inspection.commodity or 'N/A'}")
            print(f"  Actual folder: {actual_folder_name}")
            print(f"  Full path: {found_folder}")
            print(f"  Files: {len(lab_files)} lab, {len(rfi_files)} rfi, {len(invoice_files)} invoice")

            # Show sample files
            if lab_files:
                print(f"  Lab files:")
                for f in lab_files[:2]:
                    print(f"    - {f.get('commodity', 'N/A')}/{f['file']}")
            if rfi_files:
                print(f"  RFI files:")
                for f in rfi_files[:2]:
                    print(f"    - {f['file']}")
            print()
        else:
            no_files_count += 1
            print(f"✗ [{inspection.id}] {client_name} ({date_str}) - Commodity: {inspection.commodity or 'N/A'}")
            print(f"  Expected: {base_path}/{cleaned_name}")
            print(f"  No files found")
            print()

    print("="*80)
    print(f"SUMMARY:")
    print(f"  Inspections with files: {has_files_count}")
    print(f"  Inspections without files: {no_files_count}")
    print("="*80 + "\n")

    # Now test the API endpoint directly
    print("\n" + "="*80)
    print("TESTING API ENDPOINT")
    print("="*80 + "\n")

    # Import the view function
    from main.views.core_views import list_client_folder_files
    from django.http import QueryDict
    from django.test import RequestFactory
    from django.contrib.auth.models import User

    factory = RequestFactory()

    # Get a test inspection with RAW commodity
    test_inspection = Inspection.objects.filter(
        inspection_date__gte='2025-11-01',
        commodity__icontains='RAW'
    ).first()

    if not test_inspection:
        # Try any inspection
        test_inspection = Inspection.objects.filter(
            inspection_date__gte='2025-11-01'
        ).first()

    if test_inspection:
        client_name = test_inspection.facility_client_name if test_inspection.facility_client_name else 'Unknown'
        print(f"Testing API for: {client_name} ({test_inspection.inspection_date})")
        print(f"Inspection ID: {test_inspection.id}\n")

        # Create request
        request = factory.get('/list-client-folder-files/')
        request.user = User.objects.first()
        request.GET = QueryDict(mutable=True)
        request.GET['client_name'] = client_name
        request.GET['date'] = test_inspection.inspection_date.strftime('%Y-%m-%d')
        request.GET['inspection_id'] = str(test_inspection.id)

        # Call the view
        response = list_client_folder_files(request)

        if response.status_code == 200:
            data = json.loads(response.content)

            print(f"API Response:")
            print(f"  Success: {data.get('success')}")

            files = data.get('files', {})
            print(f"  File categories: {list(files.keys())}")

            for category, file_list in files.items():
                print(f"  {category}: {len(file_list)} files")
                if category == 'lab' and file_list:
                    print(f"    Files:")
                    for file_info in file_list[:3]:
                        print(f"      - {file_info.get('name')}")
        else:
            print(f"API Error: {response.status_code}")
            print(response.content)

        print("\n" + "="*80)

if __name__ == '__main__':
    test_lab_file_detection()
