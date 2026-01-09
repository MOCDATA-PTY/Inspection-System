#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test inspection sync with internal_account_code fix
"""

import os
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()

from django.contrib.auth.models import User
from main.services.google_sheets_service import GoogleSheetsService
from main.models import FoodSafetyAgencyInspection

def test_sync():
    """Test the sync and verify internal_account_code is populated"""

    print(f"\n{'='*100}")
    print(f"TESTING INSPECTION SYNC WITH INTERNAL_ACCOUNT_CODE FIX")
    print(f"{'='*100}\n")

    # Create mock request
    class MockRequest:
        def __init__(self):
            superusers = User.objects.filter(is_superuser=True)
            if superusers.exists():
                self.user = superusers.first()
            elif User.objects.exists():
                self.user = User.objects.first()
            else:
                self.user = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123'
                )
            self.session = {}
            self.method = 'POST'
            self.headers = {}

        def session_set_expiry(self, timeout):
            pass

        def session_save(self):
            pass

    request = MockRequest()
    print(f"Using user: {request.user.username}\n")

    # Initialize Google Sheets Service
    sheets_service = GoogleSheetsService()

    # Run the sync
    print("Starting sync...\n")
    result = sheets_service.populate_inspections_table(request)

    if result.get('success'):
        print(f"\n{'='*100}")
        print(f"SYNC COMPLETED SUCCESSFULLY")
        print(f"{'='*100}\n")
        print(f"Created: {result['inspections_created']} inspections\n")

        # Now test Festive specifically
        print(f"{'='*100}")
        print(f"TESTING FESTIVE INSPECTIONS")
        print(f"{'='*100}\n")

        festive_inspections = FoodSafetyAgencyInspection.objects.filter(
            client_name__icontains='Festive'
        )

        print(f"Found {festive_inspections.count()} Festive inspections\n")

        if festive_inspections.exists():
            # Check if internal_account_code is populated
            with_account_code = festive_inspections.exclude(
                internal_account_code__isnull=True
            ).exclude(internal_account_code='')

            without_account_code = festive_inspections.filter(
                internal_account_code__isnull=True
            ) | festive_inspections.filter(internal_account_code='')

            print(f"WITH internal_account_code: {with_account_code.count()}")
            print(f"WITHOUT internal_account_code: {without_account_code.count()}\n")

            if with_account_code.exists():
                print("Sample inspections WITH account code:")
                for insp in with_account_code[:5]:
                    print(f"  - {insp.date_of_inspection}: {insp.commodity} | Account: {insp.internal_account_code} | Product: {insp.product_name}")

            if without_account_code.exists():
                print("\nSample inspections WITHOUT account code:")
                for insp in without_account_code[:5]:
                    print(f"  - {insp.date_of_inspection}: {insp.commodity} | Account: {insp.internal_account_code} | Product: {insp.product_name}")

            # Group by commodity and account code
            print(f"\n{'='*100}")
            print(f"FESTIVE BY COMMODITY AND ACCOUNT CODE")
            print(f"{'='*100}\n")

            from django.db.models import Count

            summary = festive_inspections.values(
                'commodity', 'internal_account_code'
            ).annotate(count=Count('id')).order_by('commodity', 'internal_account_code')

            for item in summary:
                commodity = item['commodity']
                account = item['internal_account_code'] or 'NULL'
                count = item['count']
                print(f"{commodity:10} | {account:30} | {count:4} inspections")

        print(f"\n{'='*100}\n")

        return True
    else:
        print(f"\n{'='*100}")
        print(f"SYNC FAILED")
        print(f"{'='*100}\n")
        print(f"Error: {result.get('error', 'Unknown error')}\n")
        return False


if __name__ == "__main__":
    try:
        success = test_sync()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
