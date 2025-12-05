#!/usr/bin/env python
"""
List all sheets/tabs in a Google Spreadsheet
"""
import pickle
import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Read-only scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SPREADSHEET_ID = '1Fy7HuSCb2h_62xTuwcjmvEd5YX8KLB8B3CWG_70FTdw'

def main():
    """List all sheets in the spreadsheet"""
    creds = None

    # Check for existing token
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, refresh if possible
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid credentials found.")
            return

    # Build service
    service = build('sheets', 'v4', credentials=creds)

    # Get sheet metadata
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()

    print("="*80)
    print("ALL SHEETS/TABS IN THE SPREADSHEET")
    print("="*80)

    sheets = sheet_metadata.get('sheets', [])

    if not sheets:
        print('No sheets found.')
    else:
        print(f"Found {len(sheets)} sheets:\n")

        for i, sheet in enumerate(sheets, 1):
            props = sheet['properties']
            sheet_id = props['sheetId']
            sheet_name = props['title']
            row_count = props.get('gridProperties', {}).get('rowCount', 'Unknown')
            col_count = props.get('gridProperties', {}).get('columnCount', 'Unknown')

            print(f"{i}. Sheet Name: '{sheet_name}'")
            print(f"   Sheet ID (GID): {sheet_id}")
            print(f"   Dimensions: {row_count} rows x {col_count} columns")
            print(f"   URL: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={sheet_id}")
            print()

if __name__ == '__main__':
    main()
