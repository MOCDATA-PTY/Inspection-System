#!/usr/bin/env python
"""
List all sheet tabs in the Google Spreadsheet
"""
import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
import os

print("=" * 80)
print("LISTING SHEET TABS")
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

print(f"\nSpreadsheet: {spreadsheet.title}")
print(f"\nAvailable sheet tabs:")
print("-" * 80)

for i, worksheet in enumerate(spreadsheet.worksheets(), 1):
    print(f"{i}. {worksheet.title}")

print("\n" + "=" * 80)
