#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify View Files button functionality on mobile
Tests the /inspections/files/ endpoint and file detection logic
"""
import os
import django
import sys
import json
from datetime import datetime
from pathlib import Path

# Set console encoding to UTF-8 for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# Import after Django setup
from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from main.models import FoodSafetyAgencyInspection

User = get_user_model()

def create_folder_name(name):
    """Create Linux-friendly folder name - must match upload function"""
    if not name:
        return "unknown_client"
    import re
    # Remove special characters, keep only alphanumeric, spaces, hyphens, underscores
    clean_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)
    # Replace spaces and hyphens with underscores
    clean_name = clean_name.replace(' ', '_').replace('-', '_')
    # Remove consecutive underscores
    clean_name = re.sub(r'_+', '_', clean_name)
    # Remove leading/trailing underscores
    clean_name = clean_name.strip('_').lower()
    return clean_name or "unknown_client"

def test_view_files_endpoint():
    """Test the /inspections/files/ endpoint"""

    print("\n" + "="*80)
    print("VIEW FILES BUTTON - MOBILE TEST")
    print("="*80)

    # Create test client
    client = Client()

    # Get or create a test user
    try:
        user = User.objects.first()
        if not user:
            print("❌ No users found in database. Please create a user first.")
            return

        # Login
        client.force_login(user)
        print(f"✅ Logged in as: {user.username}")

    except Exception as e:
        print(f"❌ Error logging in: {e}")
        return

    # Find Beckley Brothers inspection
    print("\n" + "-"*80)
    print("SEARCHING FOR BECKLEY BROTHERS POULTRY FARM INSPECTION")
    print("-"*80)

    beckley_inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains="Beckley Brothers"
    ).order_by('-date_of_inspection')

    if not beckley_inspections.exists():
        print("❌ No Beckley Brothers inspections found in database")

        # Show available clients instead
        print("\n📋 Available clients in database:")
        clients = FoodSafetyAgencyInspection.objects.values_list('client_name', flat=True).distinct()[:10]
        for idx, client_name in enumerate(clients, 1):
            print(f"  {idx}. {client_name}")

        # Test with the first available inspection
        print("\n⚠️ Testing with first available inspection instead...")
        test_inspection = FoodSafetyAgencyInspection.objects.first()
    else:
        print(f"✅ Found {beckley_inspections.count()} Beckley Brothers inspection(s)")
        test_inspection = beckley_inspections.first()

    if not test_inspection:
        print("❌ No inspections found in database at all!")
        return

    # Display inspection details
    print("\n" + "-"*80)
    print("INSPECTION DETAILS")
    print("-"*80)
    print(f"Client Name: {test_inspection.client_name}")
    print(f"Inspection Date: {test_inspection.date_of_inspection}")
    print(f"Inspector: {test_inspection.inspector_name}")
    print(f"Commodity: {test_inspection.commodity}")

    # Generate groupId (same logic as frontend)
    inspection_date_str = test_inspection.date_of_inspection.strftime('%d/%m/%Y')
    group_id = f"{test_inspection.client_name}_{inspection_date_str}"
    print(f"Group ID: {group_id}")

    # Test folder name sanitization
    sanitized_folder = create_folder_name(test_inspection.client_name)
    print(f"Sanitized Folder Name: {sanitized_folder}")

    # Build expected file path
    year = test_inspection.date_of_inspection.strftime('%Y')
    month = test_inspection.date_of_inspection.strftime('%m')
    expected_path = os.path.join('media', 'inspection', year, month, sanitized_folder)
    print(f"Expected File Path: {expected_path}")

    # Check if folder exists
    full_path = os.path.join(os.getcwd(), expected_path)
    folder_exists = os.path.exists(full_path)
    print(f"Folder Exists: {'✅ YES' if folder_exists else '❌ NO'}")

    if folder_exists:
        # List files in folder
        try:
            files = os.listdir(full_path)
            print(f"Files in Folder: {len(files)}")
            if files:
                print("📁 Files found:")
                for file in files[:10]:  # Show first 10 files
                    print(f"  - {file}")
        except Exception as e:
            print(f"❌ Error listing files: {e}")

    # Test the API endpoint
    print("\n" + "-"*80)
    print("TESTING /inspections/files/ ENDPOINT")
    print("-"*80)

    request_data = {
        'group_id': group_id,
        'client_name': test_inspection.client_name,
        'inspection_date': inspection_date_str,
        '_force_refresh': True
    }

    print("📤 Request Data:")
    print(json.dumps(request_data, indent=2))

    try:
        response = client.post(
            '/inspections/files/',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        print(f"\n📥 Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n📥 Response Data:")
            print(json.dumps(result, indent=2))

            # Analyze response
            print("\n" + "-"*80)
            print("RESPONSE ANALYSIS")
            print("-"*80)

            if result.get('success'):
                print("✅ Success: True")

                files = result.get('files', {})
                print(f"\n📂 Files Object Type: {type(files)}")
                print(f"📂 Files Object Keys: {list(files.keys())}")

                # Check each category
                total_files = 0
                for category, file_list in files.items():
                    count = len(file_list) if isinstance(file_list, list) else 0
                    total_files += count
                    status = "✅" if count > 0 else "❌"
                    print(f"  {status} {category}: {count} file(s)")

                    if count > 0 and count <= 3:
                        for file_info in file_list:
                            print(f"      - {file_info.get('name', 'unknown')}")

                print(f"\n📊 Total Files: {total_files}")

                # Check if View Files button should turn orange
                has_rfi = len(files.get('rfi', [])) > 0
                has_invoice = len(files.get('invoice', [])) > 0
                has_any_files = total_files > 0

                print("\n🔘 Button Color Logic:")
                print(f"  RFI files exist: {'✅ YES (button should be green)' if has_rfi else '❌ NO (button should be gray)'}")
                print(f"  Invoice files exist: {'✅ YES (button should be green)' if has_invoice else '❌ NO (button should be gray)'}")
                print(f"  Any files exist: {'✅ YES (View Files should be orange)' if has_any_files else '❌ NO (View Files should stay blue/gray)'}")

                # Frontend hasFiles check
                has_files_frontend_logic = files and len(files.keys()) > 0
                print(f"\n🖥️ Frontend hasFiles Check (Object.keys(files).length > 0): {has_files_frontend_logic}")

                # More accurate check (at least one category has files)
                has_files_accurate = any(len(file_list) > 0 for file_list in files.values() if isinstance(file_list, list))
                print(f"🖥️ Accurate hasFiles Check (at least one category has files): {has_files_accurate}")

                # Verdict
                print("\n" + "-"*80)
                print("VERDICT")
                print("-"*80)

                if has_files_accurate:
                    print("✅ FILES FOUND - View Files popup should display files")
                    print("✅ View Files button should turn ORANGE")
                elif has_files_frontend_logic and not has_files_accurate:
                    print("⚠️ FILES OBJECT HAS KEYS BUT ALL ARRAYS ARE EMPTY!")
                    print("⚠️ This is the BUG - frontend thinks files exist but they don't")
                    print("❌ View Files popup will show 'No files found'")
                    print("❌ But button might incorrectly try to turn orange")
                else:
                    print("ℹ️ NO FILES FOUND - This is expected if no files uploaded yet")
                    print("ℹ️ View Files popup should show 'No files found'")
                    print("ℹ️ View Files button should stay blue/gray")

            else:
                print(f"❌ Success: False")
                print(f"❌ Error: {result.get('error', 'Unknown error')}")

        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(response.content)

    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        import traceback
        traceback.print_exc()

    # Test with multiple inspections
    print("\n" + "="*80)
    print("TESTING MULTIPLE INSPECTIONS")
    print("="*80)

    test_inspections = FoodSafetyAgencyInspection.objects.all().order_by('-date_of_inspection')[:5]

    print(f"\nTesting {test_inspections.count()} most recent inspections...\n")

    for idx, inspection in enumerate(test_inspections, 1):
        inspection_date_str = inspection.date_of_inspection.strftime('%d/%m/%Y')
        group_id = f"{inspection.client_name}_{inspection_date_str}"

        request_data = {
            'group_id': group_id,
            'client_name': inspection.client_name,
            'inspection_date': inspection_date_str
        }

        try:
            response = client.post(
                '/inspections/files/',
                data=json.dumps(request_data),
                content_type='application/json'
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    files = result.get('files', {})
                    total_files = sum(len(file_list) for file_list in files.values() if isinstance(file_list, list))
                    has_files = any(len(file_list) > 0 for file_list in files.values() if isinstance(file_list, list))

                    status = "✅" if has_files else "❌"
                    print(f"{idx}. {status} {inspection.client_name[:40]:<40} | Date: {inspection_date_str} | Files: {total_files}")
                else:
                    print(f"{idx}. ❌ {inspection.client_name[:40]:<40} | Date: {inspection_date_str} | Error: {result.get('error', 'Unknown')}")
            else:
                print(f"{idx}. ❌ {inspection.client_name[:40]:<40} | Date: {inspection_date_str} | Status: {response.status_code}")

        except Exception as e:
            print(f"{idx}. ❌ {inspection.client_name[:40]:<40} | Date: {inspection_date_str} | Exception: {str(e)[:50]}")

    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        test_view_files_endpoint()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
