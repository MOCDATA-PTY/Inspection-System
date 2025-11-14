#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test what Google Sheets service is actually pulling
"""
import os
import sys
import django

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.google_sheets_service import GoogleSheetsService

print("\n" + "="*80)
print("TEST: What Google Sheets Service Pulls")
print("="*80)

account_code_to_find = "RE-IND-RAW-NA-0222"

try:
    print("\n📊 Fetching data from Google Sheets...")
    service = GoogleSheetsService()

    # Get the spreadsheet data
    sheet = service.service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=service.spreadsheet_id,
        range='Sheet1!A:K'  # Columns A through K (includes H=account code, J=name)
    ).execute()

    values = result.get('values', [])

    if not values:
        print("❌ No data found in Google Sheets!")
    else:
        print(f"✅ Found {len(values)} rows in Google Sheets")

        # Find header row
        header = values[0] if values else []
        print(f"\n📋 Header row:")
        for idx, col in enumerate(header):
            letter = chr(65 + idx)  # A=65, B=66, etc.
            print(f"   Column {letter} ({idx}): {col}")

        # Find the account code column (should be H = index 7)
        # Find the name column (should be J = index 9)
        account_code_col = 7  # Column H (0-indexed)
        name_col = 9  # Column J (0-indexed)

        print(f"\n🔍 Searching for account code: {account_code_to_find}")

        found = False
        for idx, row in enumerate(values[1:], start=2):  # Skip header
            if len(row) > account_code_col:
                row_account_code = row[account_code_col].strip() if account_code_col < len(row) else ''

                if row_account_code == account_code_to_find:
                    found = True
                    print(f"\n✅ FOUND at row {idx}!")

                    print(f"\n   Full row data:")
                    for col_idx, value in enumerate(row):
                        letter = chr(65 + col_idx)
                        print(f"   Column {letter} ({col_idx}): {value}")

                    # Show specific columns
                    if len(row) > name_col:
                        name = row[name_col]
                        print(f"\n   🎯 Key Data:")
                        print(f"   Account Code (Column H): {row_account_code}")
                        print(f"   Client Name (Column J): '{name}'")
                        print(f"\n   👉 This is what should sync to Client table")
                        print(f"   👉 This is what should show in inspections")
                    else:
                        print(f"\n   ⚠️ Row doesn't have Column J (name)")

        if not found:
            print(f"\n❌ Account code '{account_code_to_find}' NOT FOUND in Google Sheets!")
            print(f"\n   Checked {len(values)-1} rows (excluding header)")

            # Show similar account codes
            print(f"\n   Looking for similar account codes...")
            similar = []
            for idx, row in enumerate(values[1:], start=2):
                if len(row) > account_code_col:
                    row_account_code = row[account_code_col].strip()
                    if 'RE-IND' in row_account_code or '0222' in row_account_code:
                        similar.append((idx, row_account_code, row[name_col] if len(row) > name_col else ''))

            if similar:
                print(f"\n   Found {len(similar)} similar account code(s):")
                for row_num, code, name in similar[:5]:
                    print(f"   Row {row_num}: {code} → '{name}'")
            else:
                print(f"\n   No similar account codes found")

        # Also show clients with "Ethan" in name
        print(f"\n" + "="*80)
        print(f"All Clients with 'Ethan' in Name")
        print("="*80)

        ethan_clients = []
        for idx, row in enumerate(values[1:], start=2):
            if len(row) > name_col and len(row) > account_code_col:
                name = row[name_col]
                account_code = row[account_code_col]
                if 'ethan' in name.lower():
                    ethan_clients.append((idx, account_code, name))

        if ethan_clients:
            print(f"\nFound {len(ethan_clients)} client(s):")
            for row_num, code, name in ethan_clients:
                print(f"\n   Row {row_num}:")
                print(f"   ├─ Account Code: {code}")
                print(f"   └─ Name: '{name}'")
        else:
            print(f"\n❌ No clients with 'Ethan' in name found")

except Exception as e:
    print(f"\n❌ Error fetching from Google Sheets: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80 + "\n")
