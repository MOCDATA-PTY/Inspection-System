#!/usr/bin/env python
"""
Debug script to see the actual format of data in one sheet
"""
import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
import os

print("=" * 80)
print("DEBUG SHEET FORMAT")
print("=" * 80)

# Load OAuth credentials
creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

if creds and creds.expired and creds.refresh_token:
    print("Refreshing OAuth token...")
    creds.refresh(Request())

if not creds or not creds.valid:
    print("ERROR: No valid OAuth credentials found")
    exit(1)

client = gspread.authorize(creds)

# Open the spreadsheet
sheet_url = 'https://docs.google.com/spreadsheets/d/1Fy7HuSCb2h_62xTuwcjmvEd5YX8KLB8B3CWG_70FTdw/edit'
spreadsheet = client.open_by_url(sheet_url)

# Check Gladys Manganye sheet (which has data according to the output)
worksheet = spreadsheet.worksheet('Gladys Manganye')
rows = worksheet.get_all_values()

print(f"\nSheet: Gladys Manganye")
print(f"Total rows: {len(rows)}")
print("\nFirst 10 rows:")
print("-" * 80)

for i, row in enumerate(rows[:10]):
    print(f"Row {i}: {row}")

print("\nLast 5 rows with data:")
print("-" * 80)

# Find last non-empty row
non_empty_rows = [r for r in rows if any(cell.strip() for cell in r)]
for i, row in enumerate(non_empty_rows[-5:]):
    print(f"Row {len(rows) - len(non_empty_rows) + len(non_empty_rows) - 5 + i}: {row}")

print("\n" + "=" * 80)
