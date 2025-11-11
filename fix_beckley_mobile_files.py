#!/usr/bin/env python3
"""
Fix Beckley Brothers files in mobile_* folder by moving them to the correct folder
and updating the database accordingly.
"""

import os
import sys
import django
import shutil
from pathlib import Path

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection
from datetime import datetime
from django.utils import timezone

def main():
    print("\n" + "=" * 80)
    print("FIX BECKLEY BROTHERS MOBILE FILES")
    print("=" * 80)

    # Source folder (where files currently are)
    source_folder = os.path.join(
        settings.MEDIA_ROOT,
        'inspection',
        '2025',
        'November',
        'mobile_beckley_brothers_poultry_farm'
    )

    # Destination folder (where files should be)
    dest_folder = os.path.join(
        settings.MEDIA_ROOT,
        'inspection',
        '2025',
        'November',
        'beckley_brothers_poultry_farm'
    )

    print(f"\nSource folder: {source_folder}")
    print(f"Destination folder: {dest_folder}")

    if not os.path.exists(source_folder):
        print(f"❌ Source folder doesn't exist: {source_folder}")
        return

    # Create destination folder if it doesn't exist
    os.makedirs(dest_folder, exist_ok=True)
    print(f"✅ Destination folder ready: {dest_folder}")

    # Process RFI files
    source_rfi_dir = os.path.join(source_folder, 'rfi')
    dest_rfi_dir = os.path.join(dest_folder, 'rfi')

    if os.path.exists(source_rfi_dir):
        os.makedirs(dest_rfi_dir, exist_ok=True)
        for filename in os.listdir(source_rfi_dir):
            if filename.endswith('.pdf'):
                # Remove 'mobile-' prefix from filename
                new_filename = filename.replace('mobile-', '')
                source_file = os.path.join(source_rfi_dir, filename)
                dest_file = os.path.join(dest_rfi_dir, new_filename)

                print(f"\n📄 Moving RFI file:")
                print(f"   From: {filename}")
                print(f"   To:   {new_filename}")

                shutil.move(source_file, dest_file)
                print(f"   ✅ Moved successfully")

    # Process Invoice files
    source_invoice_dir = os.path.join(source_folder, 'invoice')
    dest_invoice_dir = os.path.join(dest_folder, 'invoice')

    if os.path.exists(source_invoice_dir):
        os.makedirs(dest_invoice_dir, exist_ok=True)
        for filename in os.listdir(source_invoice_dir):
            if filename.endswith('.pdf'):
                # Remove 'mobile-' prefix from filename
                new_filename = filename.replace('mobile-', '')
                source_file = os.path.join(source_invoice_dir, filename)
                dest_file = os.path.join(dest_invoice_dir, new_filename)

                print(f"\n📄 Moving Invoice file:")
                print(f"   From: {filename}")
                print(f"   To:   {new_filename}")

                shutil.move(source_file, dest_file)
                print(f"   ✅ Moved successfully")

    # Clean up empty mobile folder
    try:
        if os.path.exists(source_rfi_dir) and not os.listdir(source_rfi_dir):
            os.rmdir(source_rfi_dir)
            print(f"\n🗑️  Removed empty folder: {source_rfi_dir}")

        if os.path.exists(source_invoice_dir) and not os.listdir(source_invoice_dir):
            os.rmdir(source_invoice_dir)
            print(f"🗑️  Removed empty folder: {source_invoice_dir}")

        if os.path.exists(source_folder) and not os.listdir(source_folder):
            os.rmdir(source_folder)
            print(f"🗑️  Removed empty folder: {source_folder}")
    except OSError as e:
        print(f"⚠️  Could not remove folder: {e}")

    # Update database to mark files as uploaded
    print(f"\n" + "=" * 80)
    print("UPDATING DATABASE")
    print("=" * 80)

    date_obj = datetime(2025, 11, 7).date()
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains='Beckley',
        date_of_inspection=date_obj
    )

    if inspections.exists():
        current_time = timezone.now()
        updated_count = inspections.update(
            rfi_uploaded_by_id=1,  # System user
            rfi_uploaded_date=current_time,
            invoice_uploaded_by_id=1,  # System user
            invoice_uploaded_date=current_time
        )
        print(f"✅ Updated {updated_count} inspection(s) in database")

        for insp in inspections:
            print(f"\n   Client: {insp.client_name}")
            print(f"   Date: {insp.date_of_inspection}")
            print(f"   RFI uploaded: ✅")
            print(f"   Invoice uploaded: ✅")
    else:
        print("❌ No matching inspections found in database")

    print(f"\n" + "=" * 80)
    print("DONE! Files moved and database updated.")
    print("Desktop should now show green buttons for RFI and Invoice.")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
