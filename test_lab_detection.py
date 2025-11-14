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

    # Get recent inspections with lab commodities
    inspections = Inspection.objects.filter(
        date__gte='2025-11-01'
    ).select_related('client').order_by('-date')[:50]

    print(f"Testing {len(inspections)} recent inspections...\n")

    lab_count = 0
    no_lab_count = 0

    for inspection in inspections:
        # Check if inspection has RAW commodity (which should have lab files)
        if inspection.commodities and 'RAW' in inspection.commodities.upper():
            client_name = inspection.client.name
            date_str = inspection.date.strftime('%Y-%m-%d')

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
            year = inspection.date.strftime('%Y')
            month = inspection.date.strftime('%B')

            base_path = f'/root/Inspection-System/media/inspection/{year}/{month}'

            # Check multiple folder variations
            folder_variations = [
                cleaned_name,
                f"mobile_{cleaned_name}"
            ]

            found_files = []
            found_folder = None

            for folder_var in folder_variations:
                folder_path = os.path.join(base_path, folder_var, 'Compliance')

                if os.path.exists(folder_path):
                    found_folder = folder_path
                    # Check all commodity subfolders
                    for commodity in os.listdir(folder_path):
                        commodity_path = os.path.join(folder_path, commodity)
                        if os.path.isdir(commodity_path):
                            for filename in os.listdir(commodity_path):
                                if os.path.isfile(os.path.join(commodity_path, filename)):
                                    filename_lower = filename.lower()
                                    # Check if it's a lab file
                                    if ('lab' in filename_lower or
                                        filename_lower.startswith('fsl-') or
                                        filename_lower.startswith('lab-')):
                                        found_files.append({
                                            'file': filename,
                                            'commodity': commodity,
                                            'path': os.path.join(commodity_path, filename)
                                        })

            if found_files:
                lab_count += 1
                print(f"✓ [{inspection.id}] {client_name} ({date_str})")
                print(f"  Folder: {found_folder}")
                print(f"  Lab files found: {len(found_files)}")
                for file_info in found_files[:3]:  # Show first 3
                    print(f"    - {file_info['commodity']}/{file_info['file']}")
                if len(found_files) > 3:
                    print(f"    ... and {len(found_files) - 3} more")
                print()
            else:
                no_lab_count += 1
                print(f"✗ [{inspection.id}] {client_name} ({date_str})")
                print(f"  Expected folder: {base_path}/{cleaned_name}")
                print(f"  No lab files found")
                print()

    print("="*80)
    print(f"SUMMARY:")
    print(f"  Inspections with lab files: {lab_count}")
    print(f"  Inspections without lab files: {no_lab_count}")
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

    # Get a test inspection
    test_inspection = Inspection.objects.filter(
        date__gte='2025-11-01',
        commodities__icontains='RAW'
    ).select_related('client').first()

    if test_inspection:
        print(f"Testing API for: {test_inspection.client.name} ({test_inspection.date})")
        print(f"Inspection ID: {test_inspection.id}\n")

        # Create request
        request = factory.get('/list-client-folder-files/')
        request.user = User.objects.first()
        request.GET = QueryDict(mutable=True)
        request.GET['client_name'] = test_inspection.client.name
        request.GET['date'] = test_inspection.date.strftime('%Y-%m-%d')
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
