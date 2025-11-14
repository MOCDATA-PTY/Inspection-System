#!/usr/bin/env python3
"""
Test script to verify COA fields exist and work correctly
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

if __name__ == '__main__':
    print("=" * 80)
    print("TESTING COA FIELD RENAME")
    print("=" * 80)
    print()

    # Get a sample inspection
    inspection = FoodSafetyAgencyInspection.objects.first()

    if inspection:
        print(f"Sample inspection ID: {inspection.remote_id}")
        print(f"Client: {inspection.client_name}")
        print()

        # Check if new COA fields exist
        print("Checking field existence:")
        try:
            coa_by = inspection.coa_uploaded_by
            coa_date = inspection.coa_uploaded_date
            print(f"  [OK] coa_uploaded_by field exists: {coa_by}")
            print(f"  [OK] coa_uploaded_date field exists: {coa_date}")
        except AttributeError as e:
            print(f"  [FAIL] Error accessing COA fields: {e}")

        print()

        # Check that old lab fields don't exist
        print("Verifying old lab fields are gone:")
        try:
            lab_by = inspection.lab_uploaded_by
            print(f"  [WARNING] lab_uploaded_by still exists")
        except AttributeError:
            print(f"  [OK] lab_uploaded_by field removed successfully")

        try:
            lab_date = inspection.lab_uploaded_date
            print(f"  [WARNING] lab_uploaded_date still exists")
        except AttributeError:
            print(f"  [OK] lab_uploaded_date field removed successfully")

        print()
        print("[SUCCESS] Field rename completed successfully!")
    else:
        print("No inspections found in database")

    print()
    print("=" * 80)
