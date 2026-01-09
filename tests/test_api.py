"""
Test what the API returns for Avonlea Farm CC files
"""

import os
import django
import sys
import json

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.views.core_views import get_inspection_files_local


def test_api_response():
    """Test what get_inspection_files_local returns"""

    print("\n" + "="*100)
    print("TESTING API RESPONSE FOR AVONLEA FARM CC")
    print("="*100 + "\n")

    client_name = "Avonlea Farm CC"
    inspection_date = "2025-11-17"

    print(f"Client: {client_name}")
    print(f"Date: {inspection_date}\n")

    # Call the function
    files = get_inspection_files_local(client_name, inspection_date, force_refresh=True)

    print("API Response:")
    print(json.dumps(files, indent=2, default=str))

    # Check RFI files specifically
    if 'rfi' in files and files['rfi']:
        print("\n" + "-"*100)
        print("RFI FILES FOUND:")
        print("-"*100)
        for idx, file in enumerate(files['rfi'], 1):
            print(f"\nFile #{idx}:")
            for key, value in file.items():
                print(f"  {key}: {value}")

            # Check if relative_path exists
            if 'relative_path' in file:
                print(f"\n  [OK] Has 'relative_path' field: {file['relative_path']}")
            else:
                print(f"\n  [ERROR] Missing 'relative_path' field!")
                print(f"  Available fields: {list(file.keys())}")
    else:
        print("\n[ERROR] No RFI files found in response!")

    print("\n" + "="*100 + "\n")


if __name__ == "__main__":
    try:
        test_api_response()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
