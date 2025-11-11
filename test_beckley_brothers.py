#!/usr/bin/env python3
"""
Diagnostic test for Beckley Brothers Poultry Farm
Desktop shows RED/GREY but mobile shows GREEN
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection
import re


def sanitize_client_name(client_name):
    """Sanitize client name to match folder structure"""
    if not client_name:
        return "unknown_client"
    clean_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', client_name)
    clean_name = clean_name.replace(' ', '_').replace('-', '_')
    clean_name = re.sub(r'_+', '_', clean_name)
    clean_name = clean_name.strip('_').lower()
    return clean_name or "unknown_client"


def main():
    print("\n" + "=" * 80)
    print("BECKLEY BROTHERS DIAGNOSTIC TEST")
    print("=" * 80)

    # Try different name variations
    name_variations = [
        "Beckley Brothers Poultry Farm",
        "Beckley Brother Poultry Farm",
        "Beckley Brothers",
        "beckley brothers poultry farm"
    ]

    inspection_date = "2025-11-07"

    for client_name in name_variations:
        print(f"\n{'='*80}")
        print(f"Testing: {client_name}")
        print(f"{'='*80}")

        # Check database
        date_obj = datetime.strptime(inspection_date, '%Y-%m-%d').date()
        inspections = FoodSafetyAgencyInspection.objects.filter(
            client_name__icontains=client_name.split()[0],
            date_of_inspection=date_obj
        )

        print(f"\n📊 Database Results:")
        if inspections.exists():
            print(f"   Found {inspections.count()} inspection(s)")
            for insp in inspections[:3]:
                print(f"\n   Client Name: {insp.client_name}")
                print(f"   Date: {insp.date_of_inspection}")
                print(f"   RFI uploaded: {insp.rfi_uploaded_by is not None}")
                print(f"   Invoice uploaded: {insp.invoice_uploaded_by is not None}")
                print(f"   COA uploaded: {insp.coa_uploaded_by is not None}")
        else:
            print(f"   No inspections found")

        # Check filesystem
        year = datetime.strptime(inspection_date, '%Y-%m-%d').strftime('%Y')
        month = datetime.strptime(inspection_date, '%Y-%m-%d').strftime('%B')
        sanitized_name = sanitize_client_name(client_name)

        print(f"\n📁 Filesystem Check:")
        print(f"   Sanitized name: {sanitized_name}")

        inspection_path = os.path.join(settings.MEDIA_ROOT, 'inspection', year, month, sanitized_name)
        print(f"   Path: {inspection_path}")
        print(f"   Exists: {os.path.exists(inspection_path)}")

        if os.path.exists(inspection_path):
            contents = os.listdir(inspection_path)
            print(f"   Contents: {contents}")

            for item in ['rfi', 'invoice', 'lab']:
                item_path = os.path.join(inspection_path, item)
                if os.path.exists(item_path):
                    files = os.listdir(item_path)
                    print(f"   {item.upper()}: {len(files)} file(s) - {files}")
                else:
                    print(f"   {item.upper()}: folder doesn't exist")

    # Search for any Beckley folders
    print(f"\n{'='*80}")
    print("SEARCHING FOR BECKLEY FOLDERS IN NOVEMBER 2025")
    print(f"{'='*80}")

    month_path = os.path.join(settings.MEDIA_ROOT, 'inspection', '2025', 'November')
    if os.path.exists(month_path):
        all_folders = [f for f in os.listdir(month_path) if os.path.isdir(os.path.join(month_path, f))]
        beckley_folders = [f for f in all_folders if 'beckley' in f.lower()]

        if beckley_folders:
            print(f"\n✅ Found {len(beckley_folders)} folder(s) with 'beckley':")
            for folder in beckley_folders:
                folder_path = os.path.join(month_path, folder)
                print(f"\n   📁 {folder}")

                # List contents
                contents = os.listdir(folder_path)
                print(f"      Contents: {contents}")

                # Check each document type
                for doc_type in ['rfi', 'invoice', 'lab', 'compliance']:
                    doc_path = os.path.join(folder_path, doc_type)
                    if os.path.exists(doc_path):
                        files = os.listdir(doc_path)
                        if files:
                            print(f"      {doc_type.upper()}: {len(files)} file(s)")
                            for f in files:
                                file_path = os.path.join(doc_path, f)
                                size = os.path.getsize(file_path)
                                print(f"         - {f} ({size:,} bytes)")
        else:
            print("   ❌ No folders found with 'beckley'")

    # Check database for all Beckley inspections
    print(f"\n{'='*80}")
    print("ALL BECKLEY INSPECTIONS IN DATABASE")
    print(f"{'='*80}")

    all_beckley = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains='beckley'
    ).values_list('client_name', flat=True).distinct()

    if all_beckley:
        print(f"\n✅ Found {len(all_beckley)} unique client name(s):")
        for name in all_beckley:
            print(f"   - {name}")
    else:
        print("   ❌ No Beckley clients found in database")


if __name__ == '__main__':
    main()
