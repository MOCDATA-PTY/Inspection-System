"""
Sync client data from Google Sheets to ClientAllocation model
Reads client information from the Google Sheet and updates/creates ClientAllocation records
"""
import os
import sys
import django
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import ClientAllocation

# Google Sheets configuration
SPREADSHEET_ID = '1gHOowl6YqfVPU3wAxz3jQRNwQwRAC4Kja8_0zqG-n9w'  # Update with your sheet ID
SHEET_NAME = 'Internal Account Code Generator'  # Update with your sheet name
RANGE_NAME = f"{SHEET_NAME}!A2:N"  # Read from row 2 (skip header) to column N
TOKEN_FILE = 'token.pickle'

# Column mapping (0-indexed)
COL_CLIENT_ID = 0  # Column A
COL_FACILITY_TYPE = 1  # Column B
COL_GROUP_TYPE = 2  # Column C
COL_COMMODITY = 3  # Column D
COL_PROVINCE = 4  # Column E
COL_CORPORATE_GROUP = 5  # Column F
COL_OTHER = 6  # Column G
COL_INTERNAL_ACCOUNT_CODE = 7  # Column H
COL_ALLOCATED = 8  # Column I
COL_ECLICK_NAME = 9  # Column J
COL_REPRESENTATIVE_EMAIL = 10  # Column K
COL_PHONE_NUMBER = 11  # Column L
COL_DUPLICATES = 12  # Column M
COL_ACTIVE_STATUS = 13  # Column N

def get_google_sheets_service():
    """Authenticate and return Google Sheets service."""
    creds = None

    # Load existing credentials
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        print("Refreshing expired token...")
        creds.refresh(Request())
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    if not creds or not creds.valid:
        print("ERROR: No valid credentials found!")
        print("Please run: python tests/authenticate_google_simple.py")
        sys.exit(1)

    return build('sheets', 'v4', credentials=creds)

def parse_boolean(value):
    """Parse various boolean representations."""
    if value is None or value == '':
        return False
    if isinstance(value, bool):
        return value
    value_str = str(value).strip().upper()
    return value_str in ['TRUE', 'YES', '1', 'Y']

def parse_int(value):
    """Safely parse integer values."""
    if value is None or value == '':
        return None
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None

def sync_clients_from_sheet():
    """Read Google Sheet and sync to ClientAllocation model."""
    print("=" * 100)
    print("SYNCING CLIENT DATA FROM GOOGLE SHEETS")
    print("=" * 100)

    # Get Google Sheets service
    print("\n[1] Authenticating with Google Sheets...")
    service = get_google_sheets_service()
    print("✓ Authenticated successfully")

    # Read data from sheet
    print(f"\n[2] Reading data from sheet: {SHEET_NAME}")
    print(f"    Range: {RANGE_NAME}")
    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()

        values = result.get('values', [])
        print(f"✓ Found {len(values)} rows")
    except Exception as e:
        print(f"✗ ERROR reading sheet: {e}")
        return

    if not values:
        print("✗ No data found in sheet")
        return

    # Process each row
    print(f"\n[3] Processing rows...")
    created_count = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0

    for i, row in enumerate(values, start=2):  # Start at row 2 (row 1 is header)
        # Pad row to ensure we have enough columns
        while len(row) < 14:
            row.append('')

        # Extract data
        client_id = parse_int(row[COL_CLIENT_ID])
        facility_type = row[COL_FACILITY_TYPE].strip() if len(row) > COL_FACILITY_TYPE else ''
        group_type = row[COL_GROUP_TYPE].strip() if len(row) > COL_GROUP_TYPE else ''
        commodity = row[COL_COMMODITY].strip() if len(row) > COL_COMMODITY else ''
        province = row[COL_PROVINCE].strip() if len(row) > COL_PROVINCE else ''
        corporate_group = row[COL_CORPORATE_GROUP].strip() if len(row) > COL_CORPORATE_GROUP else ''
        other = row[COL_OTHER].strip() if len(row) > COL_OTHER else ''
        internal_account_code = row[COL_INTERNAL_ACCOUNT_CODE].strip() if len(row) > COL_INTERNAL_ACCOUNT_CODE else ''
        allocated = parse_boolean(row[COL_ALLOCATED]) if len(row) > COL_ALLOCATED else False
        eclick_name = row[COL_ECLICK_NAME].strip() if len(row) > COL_ECLICK_NAME else ''
        representative_email = row[COL_REPRESENTATIVE_EMAIL].strip() if len(row) > COL_REPRESENTATIVE_EMAIL else ''
        phone_number = row[COL_PHONE_NUMBER].strip() if len(row) > COL_PHONE_NUMBER else ''
        duplicates = row[COL_DUPLICATES].strip() if len(row) > COL_DUPLICATES else ''
        active_status = row[COL_ACTIVE_STATUS].strip() if len(row) > COL_ACTIVE_STATUS else ''

        # Skip if no client ID or e-Click name
        if not client_id or not eclick_name:
            skipped_count += 1
            continue

        try:
            # Find or create ClientAllocation by eclick_name
            client, created = ClientAllocation.objects.get_or_create(
                client_id=client_id,
                defaults={
                    'eclick_name': eclick_name,
                    'facility_type': facility_type or None,
                    'group_type': group_type or None,
                    'commodity': commodity or None,
                    'province': province or None,
                    'corporate_group': corporate_group or None,
                    'other': other or None,
                    'internal_account_code': internal_account_code or None,
                    'allocated': allocated,
                    'representative_email': representative_email or None,
                    'phone_number': phone_number or None,
                    'duplicates': duplicates or None,
                    'active_status': active_status or None,
                    'manually_added': False,  # Synced from sheet
                }
            )

            if created:
                created_count += 1
                print(f"  Row {i}: ✓ Created: {eclick_name} (ID: {client_id})")
            else:
                # Update existing record
                client.eclick_name = eclick_name
                client.facility_type = facility_type or None
                client.group_type = group_type or None
                client.commodity = commodity or None
                client.province = province or None
                client.corporate_group = corporate_group or None
                client.other = other or None
                client.internal_account_code = internal_account_code or None
                client.allocated = allocated
                client.representative_email = representative_email or None
                client.phone_number = phone_number or None
                client.duplicates = duplicates or None
                client.active_status = active_status or None
                client.save()
                updated_count += 1
                print(f"  Row {i}: ✓ Updated: {eclick_name} (ID: {client_id})")

        except Exception as e:
            error_count += 1
            print(f"  Row {i}: ✗ ERROR: {eclick_name} - {e}")

    # Summary
    print("\n" + "=" * 100)
    print("SYNC SUMMARY")
    print("=" * 100)
    print(f"Total rows processed: {len(values)}")
    print(f"✓ Created: {created_count}")
    print(f"✓ Updated: {updated_count}")
    print(f"⊘ Skipped: {skipped_count} (no client ID or name)")
    print(f"✗ Errors: {error_count}")
    print("=" * 100)

    # Show sample of what was synced
    if created_count > 0 or updated_count > 0:
        print("\nSample of synced data:")
        recent_clients = ClientAllocation.objects.filter(manually_added=False).order_by('-last_synced')[:5]
        for client in recent_clients:
            print(f"  • {client.eclick_name}")
            print(f"    Commodity: {client.commodity}")
            print(f"    Province: {client.province}")
            print(f"    Corporate Group: {client.corporate_group}")
            print(f"    Internal Account Code: {client.internal_account_code}")
            print(f"    Allocated: {client.allocated}")
            print()

if __name__ == '__main__':
    sync_clients_from_sheet()
