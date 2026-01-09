#!/usr/bin/env python3
"""
Comprehensive test script for Kings Meat Deli Castle Walk inspection
Tests all aspects: database, filesystem, API endpoints, and file detection
"""

import os
import sys
import django
import json
from datetime import datetime
from pathlib import Path

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection, Client
import re


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def sanitize_client_name(client_name):
    """Sanitize client name to match folder structure"""
    if not client_name:
        return "unknown_client"
    # Remove special characters, keep only alphanumeric, spaces, hyphens, underscores
    clean_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', client_name)
    # Replace spaces and hyphens with underscores
    clean_name = clean_name.replace(' ', '_').replace('-', '_')
    # Remove consecutive underscores
    clean_name = re.sub(r'_+', '_', clean_name)
    # Remove leading/trailing underscores
    clean_name = clean_name.strip('_').lower()
    return clean_name or "unknown_client"


def test_database_info():
    """Test 1: Check database for Kings Meat Deli"""
    print_section("TEST 1: DATABASE INFORMATION")

    client_name = "Kings Meat Deli Castle Walk"
    inspection_date = "2025-11-07"

    # Check if client exists
    try:
        client = Client.objects.get(name=client_name)
        print(f"✅ Client found in database:")
        print(f"   - Name: {client.name}")
        print(f"   - Client ID: {client.client_id}")
        print(f"   - Email: {client.email}")
        print(f"   - Created: {client.created_at}")
    except Client.DoesNotExist:
        print(f"❌ Client '{client_name}' NOT found in database")
        print("\n   Searching for similar names...")
        similar = Client.objects.filter(name__icontains="Kings").filter(name__icontains="Meat")
        for c in similar:
            print(f"   - Found: {c.name}")
    except Exception as e:
        print(f"❌ Error checking client: {e}")

    # Check for inspections
    print(f"\n🔍 Searching for inspections on {inspection_date}...")
    try:
        date_obj = datetime.strptime(inspection_date, '%Y-%m-%d').date()
        inspections = FoodSafetyAgencyInspection.objects.filter(
            client_name=client_name,
            date_of_inspection=date_obj
        )

        if inspections.exists():
            print(f"✅ Found {inspections.count()} inspection(s):")
            for insp in inspections:
                print(f"\n   Inspection ID: {insp.id}")
                print(f"   - Client: {insp.client_name}")
                print(f"   - Date: {insp.date_of_inspection}")
                print(f"   - Inspector: {insp.inspector_name} (ID: {insp.inspector_id})")
                print(f"   - RFI uploaded: {insp.rfi_uploaded_by is not None}")
                print(f"   - RFI uploader: {insp.rfi_uploaded_by}")
                print(f"   - Invoice uploaded: {insp.invoice_uploaded_by is not None}")
                print(f"   - Invoice uploader: {insp.invoice_uploaded_by}")
                print(f"   - Lab uploaded: Lab field doesn't exist in model")
        else:
            print(f"❌ No inspections found for {client_name} on {inspection_date}")
            print("\n   Searching all dates for this client...")
            all_inspections = FoodSafetyAgencyInspection.objects.filter(
                client_name=client_name
            ).order_by('-date_of_inspection')[:5]
            if all_inspections.exists():
                print(f"   Found {all_inspections.count()} inspection(s) for this client:")
                for insp in all_inspections:
                    print(f"   - {insp.date_of_inspection}")
            else:
                print("   No inspections found for this client at all")
    except Exception as e:
        print(f"❌ Error checking inspections: {e}")
        import traceback
        traceback.print_exc()


def test_filesystem():
    """Test 2: Check filesystem for files"""
    print_section("TEST 2: FILESYSTEM CHECK")

    client_name = "Kings Meat Deli Castle Walk"
    inspection_date = "2025-11-07"

    date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
    year = date_obj.strftime('%Y')
    month = date_obj.strftime('%B')

    sanitized_name = sanitize_client_name(client_name)

    print(f"📁 Client name: {client_name}")
    print(f"📁 Sanitized name: {sanitized_name}")
    print(f"📁 Year: {year}")
    print(f"📁 Month: {month}")

    base_path = settings.MEDIA_ROOT
    inspection_path = os.path.join(base_path, 'inspection', year, month, sanitized_name)

    print(f"\n📍 Expected folder path:")
    print(f"   {inspection_path}")
    print(f"   Exists: {os.path.exists(inspection_path)}")

    if os.path.exists(inspection_path):
        print(f"\n📂 Folder contents:")
        try:
            contents = os.listdir(inspection_path)
            if contents:
                for item in contents:
                    item_path = os.path.join(inspection_path, item)
                    if os.path.isdir(item_path):
                        print(f"   📁 {item}/ (directory)")
                        # List files in subdirectory
                        try:
                            files = os.listdir(item_path)
                            for f in files:
                                file_path = os.path.join(item_path, f)
                                if os.path.isfile(file_path):
                                    size = os.path.getsize(file_path)
                                    modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                                    print(f"      📄 {f}")
                                    print(f"         Size: {size:,} bytes")
                                    print(f"         Modified: {modified}")
                        except Exception as e:
                            print(f"      ❌ Error listing files: {e}")
                    else:
                        print(f"   📄 {item} (file)")
            else:
                print("   ⚠️ Folder is empty")
        except Exception as e:
            print(f"   ❌ Error listing contents: {e}")
    else:
        print("\n❌ Folder does not exist!")

        # Check if there's a mobile_ prefixed folder
        mobile_path = os.path.join(base_path, 'inspection', year, month, f'mobile_{sanitized_name}')
        print(f"\n🔍 Checking for mobile folder:")
        print(f"   {mobile_path}")
        print(f"   Exists: {os.path.exists(mobile_path)}")

        # List all folders in the month directory that might match
        month_path = os.path.join(base_path, 'inspection', year, month)
        if os.path.exists(month_path):
            print(f"\n🔍 All folders in {month}:")
            all_folders = [f for f in os.listdir(month_path) if os.path.isdir(os.path.join(month_path, f))]
            matching = [f for f in all_folders if 'king' in f.lower() and 'meat' in f.lower()]
            if matching:
                print("   Folders containing 'king' and 'meat':")
                for f in matching:
                    print(f"   - {f}")
            else:
                print("   No folders found containing 'king' and 'meat'")


def test_view_files_api():
    """Test 3: Call the View Files API"""
    print_section("TEST 3: VIEW FILES API")

    from django.test import RequestFactory
    from django.contrib.auth import get_user_model
    from main.views.core_views import get_inspection_files

    client_name = "Kings Meat Deli Castle Walk"
    inspection_date = "2025-11-07"

    print(f"📞 Calling get_inspection_files API...")
    print(f"   Client: {client_name}")
    print(f"   Date: {inspection_date}")

    try:
        # Create a mock request
        factory = RequestFactory()
        User = get_user_model()
        user = User.objects.first()

        request = factory.post('/inspections/get-inspection-files/',
                              data=json.dumps({
                                  'client_name': client_name,
                                  'inspection_date': inspection_date,
                                  '_force_refresh': True
                              }),
                              content_type='application/json')
        request.user = user

        # Call the view
        response = get_inspection_files(request)
        data = json.loads(response.content)

        print(f"\n✅ API Response:")
        print(f"   Success: {data.get('success')}")
        print(f"   Total files: {data.get('total_files', 0)}")

        if data.get('success'):
            files = data.get('files', {})
            print(f"\n📂 Files by category:")
            for category, file_list in files.items():
                if file_list:
                    print(f"   {category.upper()}: {len(file_list)} file(s)")
                    for file_info in file_list:
                        print(f"      - {file_info.get('name')}")
                        print(f"        Size: {file_info.get('size', 0):,} bytes")
                        print(f"        Modified: {file_info.get('modified')}")
        else:
            print(f"   Error: {data.get('error')}")

        print(f"\n📋 Full Response:")
        print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"❌ Error calling API: {e}")
        import traceback
        traceback.print_exc()


def test_button_color_api():
    """Test 4: Call the Button Color API"""
    print_section("TEST 4: BUTTON COLOR API (get_page_clients_file_status)")

    from django.test import RequestFactory
    from django.contrib.auth import get_user_model
    from main.views.core_views import get_page_clients_file_status

    client_name = "Kings Meat Deli Castle Walk"
    inspection_date = "2025-11-07"
    unique_key = f"{client_name}_{inspection_date}"

    print(f"📞 Calling get_page_clients_file_status API...")
    print(f"   Client: {client_name}")
    print(f"   Date: {inspection_date}")
    print(f"   Unique Key: {unique_key}")

    try:
        # Create a mock request
        factory = RequestFactory()
        User = get_user_model()
        user = User.objects.first()

        request = factory.post('/page-clients-status/',
                              data=json.dumps({
                                  'client_date_combinations': [
                                      {
                                          'client_name': client_name,
                                          'inspection_date': inspection_date,
                                          'unique_key': unique_key
                                      }
                                  ]
                              }),
                              content_type='application/json')
        request.user = user

        # Call the view
        response = get_page_clients_file_status(request)
        data = json.loads(response.content)

        print(f"\n✅ API Response:")
        print(f"   Success: {data.get('success')}")

        if data.get('success'):
            statuses = data.get('combination_statuses', {})
            print(f"   Combinations checked: {len(statuses)}")

            if unique_key in statuses:
                status_data = statuses[unique_key]
                print(f"\n📊 Status for {unique_key}:")
                print(f"   File Status: {status_data.get('file_status')}")
                print(f"   Has RFI: {status_data.get('has_rfi')}")
                print(f"   Has Invoice: {status_data.get('has_invoice')}")
                print(f"   Has Lab: {status_data.get('has_lab')}")
                print(f"   Has Retest: {status_data.get('has_retest')}")
                print(f"   Has Compliance: {status_data.get('has_compliance')}")
                print(f"   Has Occurrence: {status_data.get('has_occurrence')}")
                print(f"   Has Composition: {status_data.get('has_composition')}")
            else:
                print(f"\n❌ No status found for {unique_key}")
                print(f"   Available keys: {list(statuses.keys())}")
        else:
            print(f"   Error: {data.get('error')}")

        print(f"\n📋 Full Response:")
        print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"❌ Error calling API: {e}")
        import traceback
        traceback.print_exc()


def test_comparison():
    """Test 5: Compare results"""
    print_section("TEST 5: COMPARISON & DIAGNOSIS")

    client_name = "Kings Meat Deli Castle Walk"
    inspection_date = "2025-11-07"

    print("🔬 Analyzing results...")

    # Check database
    date_obj = datetime.strptime(inspection_date, '%Y-%m-%d').date()
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name=client_name,
        date_of_inspection=date_obj
    )
    has_inspection_record = inspections.exists()

    # Check filesystem
    year = datetime.strptime(inspection_date, '%Y-%m-%d').strftime('%Y')
    month = datetime.strptime(inspection_date, '%Y-%m-%d').strftime('%B')
    sanitized_name = sanitize_client_name(client_name)
    inspection_path = os.path.join(settings.MEDIA_ROOT, 'inspection', year, month, sanitized_name)
    folder_exists = os.path.exists(inspection_path)

    rfi_path = os.path.join(inspection_path, 'rfi')
    lab_path = os.path.join(inspection_path, 'lab')
    has_rfi_folder = os.path.exists(rfi_path)
    has_lab_folder = os.path.exists(lab_path)

    rfi_files = []
    lab_files = []
    if has_rfi_folder:
        rfi_files = [f for f in os.listdir(rfi_path) if os.path.isfile(os.path.join(rfi_path, f))]
    if has_lab_folder:
        lab_files = [f for f in os.listdir(lab_path) if os.path.isfile(os.path.join(lab_path, f))]

    print(f"\n📊 Summary:")
    print(f"   Database inspection record: {'✅ YES' if has_inspection_record else '❌ NO'}")
    print(f"   Filesystem folder exists: {'✅ YES' if folder_exists else '❌ NO'}")
    print(f"   RFI folder exists: {'✅ YES' if has_rfi_folder else '❌ NO'}")
    print(f"   RFI files count: {len(rfi_files)}")
    print(f"   Lab folder exists: {'✅ YES' if has_lab_folder else '❌ NO'}")
    print(f"   Lab files count: {len(lab_files)}")

    print(f"\n🔍 Diagnosis:")
    if len(rfi_files) > 0 and len(lab_files) > 0:
        print("   ✅ FILES EXIST - View Files button should be ORANGE")
        print("   ✅ RFI and Lab buttons should be GREEN")
        print("\n   🐛 If View Files button is RED, the issue is:")
        print("      - Frontend is not calling the button color API for this client")
        print("      - OR: Client name mismatch between HTML data attributes and API")
        print("      - OR: JavaScript is filtering out this client from the request")
    elif folder_exists:
        print("   ⚠️ FOLDER EXISTS BUT NO FILES")
        print("   This explains why View Files shows red")
    else:
        print("   ❌ FOLDER DOES NOT EXIST")
        print("   Files may be in a different location or not uploaded yet")


def main():
    """Run all tests"""
    print("\n" + "🔬" * 40)
    print("COMPREHENSIVE INSPECTION TEST: Kings Meat Deli Castle Walk")
    print("Date: 2025-11-07")
    print("🔬" * 40)

    try:
        test_database_info()
        test_filesystem()
        test_view_files_api()
        test_button_color_api()
        test_comparison()

        print_section("TEST COMPLETE")
        print("✅ All tests completed. Review results above for diagnosis.")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
