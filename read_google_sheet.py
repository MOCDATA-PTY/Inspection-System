#!/usr/bin/env python
"""
Read Google Sheet in read-only mode
"""
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Read-only scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Sheet URL: https://docs.google.com/spreadsheets/d/1Fy7HuSCb2h_62xTuwcjmvEd5YX8KLB8B3CWG_70FTdw/edit?gid=254313848#gid=254313848
SPREADSHEET_ID = '1Fy7HuSCb2h_62xTuwcjmvEd5YX8KLB8B3CWG_70FTdw'
SHEET_GID = '254313848'

def main():
    """Read Google Sheet"""
    creds = None

    # Check for existing token
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, can't proceed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid credentials found. Cannot access the sheet.")
            return

    # Build service
    service = build('sheets', 'v4', credentials=creds)

    # Get sheet metadata to find the sheet name
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', [])

    # Find the sheet with matching GID
    sheet_name = None
    for sheet in sheets:
        if str(sheet['properties']['sheetId']) == SHEET_GID:
            sheet_name = sheet['properties']['title']
            break

    if not sheet_name:
        # If GID not found, try first sheet
        sheet_name = sheets[0]['properties']['title'] if sheets else 'Sheet1'

    print(f"Reading sheet: '{sheet_name}'")
    print(f"Spreadsheet ID: {SPREADSHEET_ID}")
    print("="*80)

    # Read the sheet
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{sheet_name}'!A1:Z1000"  # Read first 1000 rows, columns A-Z
    ).execute()

    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print(f"Found {len(values)} rows")
        print("="*80)

        # Print first 50 rows
        for i, row in enumerate(values[:50], 1):
            # Pad row to have consistent columns
            row_data = '\t'.join(str(cell) for cell in row)
            print(f"Row {i}: {row_data}")

        if len(values) > 50:
            print(f"\n... and {len(values) - 50} more rows")

if __name__ == '__main__':
    main()
