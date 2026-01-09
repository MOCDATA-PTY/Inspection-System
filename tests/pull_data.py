"""
Pull Client Allocation data from Google Sheets and save to PostgreSQL database.

This script fetches data from the 'Internal Account Code Generator' Google Sheet
and syncs it to the local PostgreSQL database.

Usage:
    python pull_data.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.google_sheets_service import GoogleSheetsService
from main.models import ClientAllocation


def pull_client_allocation_data():
    """Pull data from Google Sheets and save to PostgreSQL."""

    print("=" * 70)
    print("CLIENT ALLOCATION DATA SYNC")
    print("=" * 70)
    print()

    try:
        # Initialize Google Sheets service
        print(">> Initializing Google Sheets service...")
        sheets_service = GoogleSheetsService()

        # Spreadsheet details
        spreadsheet_id = "1iNULGBAzJ9n2ZulxwP8ZZZbwcPhj7X6e6rPwYqtI_fM"
        sheet_name = "Internal Account Code Generator"
        range_name = f"'{sheet_name}'!A2:N"

        print(f">> Fetching data from Google Sheets...")
        print(f"   Spreadsheet ID: {spreadsheet_id}")
        print(f"   Sheet Name: {sheet_name}")
        print(f"   Range: {range_name}")
        print()

        # Fetch all data from row 2 onwards (row 1 is headers)
        # Fetch columns A through N (14 columns)
        sheet_data = sheets_service.get_sheet_data(spreadsheet_id, range_name, request=None)

        if not sheet_data:
            print("WARNING: No data found in Google Sheets.")
            return

        print(f"SUCCESS: Fetched {len(sheet_data)} rows from Google Sheets")
        print()

        # Clear existing data before syncing
        print(">> Clearing existing database records...")
        deleted_count = ClientAllocation.objects.all().count()
        ClientAllocation.objects.all().delete()
        print(f"   Deleted {deleted_count} existing records")
        print()

        # Process and prepare bulk data (MUCH faster than individual creates)
        print(">> Preparing data for bulk insert...")
        bulk_records = []
        skip_count = 0

        for idx, row in enumerate(sheet_data, start=2):  # Start at 2 because row 1 is headers
            # Pad the row with empty strings if it has fewer than 14 columns
            while len(row) < 14:
                row.append('')

            # Skip rows without a client ID
            if not row[0] or str(row[0]).strip() == '':
                skip_count += 1
                continue

            try:
                client_id = int(row[0])
            except (ValueError, TypeError):
                print(f"   WARNING: Row {idx}: Invalid Client ID '{row[0]}' - skipping")
                skip_count += 1
                continue

            # Convert "TRUE"/"FALSE" string to boolean for allocated field
            allocated = str(row[8]).strip().upper() == 'TRUE' if row[8] else False

            # Create ClientAllocation object (not yet saved to database)
            bulk_records.append(ClientAllocation(
                client_id=client_id,
                facility_type=row[1] if row[1] else None,
                group_type=row[2] if row[2] else None,
                commodity=row[3] if row[3] else None,
                province=row[4] if row[4] else None,
                corporate_group=row[5] if row[5] else None,
                other=row[6] if row[6] else None,
                internal_account_code=row[7] if row[7] else None,
                allocated=allocated,
                eclick_name=row[9] if row[9] else None,
                representative_email=row[10] if row[10] else None,
                phone_number=row[11] if row[11] else None,
                duplicates=row[12] if row[12] else None,
                active_status=row[13] if row[13] else None,
            ))

        # Bulk insert all records in a single optimized transaction
        print(">> Performing bulk database insert...")
        from django.db import transaction

        with transaction.atomic():
            # Bulk create all records (batch_size=500 optimizes for PostgreSQL)
            ClientAllocation.objects.bulk_create(bulk_records, batch_size=500)

        sync_count = len(bulk_records)

        print()
        print("=" * 70)
        print("SYNC COMPLETE")
        print("=" * 70)
        print(f"SUCCESS: Synced {sync_count} client allocation records")
        if skip_count > 0:
            print(f"WARNING: Skipped {skip_count} invalid/empty rows")
        print()

    except ConnectionError as e:
        print()
        print("=" * 70)
        print("CONNECTION ERROR")
        print("=" * 70)
        print(f"Cannot connect to Google Sheets: {str(e)}")
        print("Please check your internet connection and try again.")
        print()

    except Exception as e:
        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print(f"Error syncing data: {str(e)}")
        print()
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    pull_client_allocation_data()
