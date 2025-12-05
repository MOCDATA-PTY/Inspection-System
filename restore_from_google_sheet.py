#!/usr/bin/env python
"""
Restore KM and Hours data from Google Sheet for specific inspector
Reads October-December 2025 data directly from the sheet
"""
import os
import sys
import pickle
import django
from datetime import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db import transaction

# Google Sheets configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1Fy7HuSCb2h_62xTuwcjmvEd5YX8KLB8B3CWG_70FTdw'

# Column indices (0-based)
COL_DATE = 4  # Column E (Date)
COL_FACILITY = 5  # Column F (Facility / Client Name)
COL_COMMODITY = 7  # Column H (Commodity)
COL_HOURS = 12  # Column M (Normal Hours)
COL_KM = 13  # Column N (Kilometres Traveled)

def get_google_sheets_service():
    """Get authenticated Google Sheets service"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid credentials found.")
            return None

    return build('sheets', 'v4', credentials=creds)

def parse_date(date_str):
    """Parse date from various formats"""
    if not date_str or not isinstance(date_str, str):
        return None

    date_str = date_str.strip()
    if not date_str:
        return None

    # Try DD/MM/YYYY format
    try:
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except:
        pass

    # Try other formats
    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']:
        try:
            return datetime.strptime(date_str, fmt).date()
        except:
            continue

    return None

def extract_oct_dec_data(sheet_name, service):
    """Extract October-December 2025 data from a specific sheet"""
    print(f"\nReading sheet: '{sheet_name}'")

    # Read all data from the sheet
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{sheet_name}'!A1:Z2000"
    ).execute()

    values = result.get('values', [])

    if not values:
        print("  No data found")
        return []

    data = []
    in_target_months = False

    for row_num, row in enumerate(values, 1):
        # Skip if row doesn't have enough columns
        if len(row) <= max(COL_DATE, COL_FACILITY, COL_HOURS, COL_KM):
            continue

        # Get date
        date_str = row[COL_DATE] if COL_DATE < len(row) else None
        if not date_str:
            continue

        # Check if this is a month header (like "October 2025")
        date_str_lower = str(date_str).lower()
        if 'october' in date_str_lower or 'november' in date_str_lower or 'december' in date_str_lower:
            if '2025' in date_str_lower:
                in_target_months = True
                print(f"  Found month section: {date_str}")
            continue

        # Stop if we hit a different month section
        if 'january' in date_str_lower or 'february' in date_str_lower:
            if '2026' in date_str_lower:
                break

        # Parse the date
        date_obj = parse_date(date_str)
        if not date_obj:
            continue

        # Check if it's October-December 2025
        if not (date_obj.year == 2025 and date_obj.month >= 10 and date_obj.month <= 12):
            continue

        # Get facility name
        facility = row[COL_FACILITY] if COL_FACILITY < len(row) else None
        if not facility or not facility.strip():
            continue

        # Get commodity
        commodity = row[COL_COMMODITY] if COL_COMMODITY < len(row) else None
        if not commodity or not commodity.strip():
            commodity = 'RAW'  # Default

        # Get hours and km
        hours_str = row[COL_HOURS] if COL_HOURS < len(row) else None
        km_str = row[COL_KM] if COL_KM < len(row) else None

        # Parse hours
        try:
            hours = float(hours_str) if hours_str and str(hours_str).strip() else None
        except:
            hours = None

        # Parse km
        try:
            km = float(km_str) if km_str and str(km_str).strip() else None
        except:
            km = None

        # Only include if we have both hours and km
        if hours and km:
            data.append({
                'date': date_obj,
                'facility': facility.strip(),
                'commodity': commodity.strip().upper(),
                'hours': hours,
                'km': km,
                'row': row_num
            })

    print(f"  Found {len(data)} entries with hours and km in Oct-Dec 2025")
    return data

def update_inspections(inspector_name, db_inspector_name, data):
    """Update inspections in the database"""
    print(f"\n{'='*80}")
    print(f"UPDATING DATABASE FOR {inspector_name.upper()}")
    print(f"Database inspector name: {db_inspector_name}")
    print(f"{'='*80}")

    updated_count = 0
    not_found = []

    with transaction.atomic():
        for entry in data:
            try:
                # Find matching inspections using flexible matching
                facility_search = entry['facility'].replace("'", "").split()[0]

                inspections = FoodSafetyAgencyInspection.objects.filter(
                    inspector_name__iexact=db_inspector_name,
                    date_of_inspection=entry['date'],
                    client_name__icontains=facility_search,
                    commodity__iexact=entry['commodity']
                )

                if inspections.exists():
                    inspections.update(
                        km_traveled=entry['km'],
                        hours=entry['hours']
                    )
                    count = inspections.count()
                    updated_count += count
                    print(f"[OK] Updated {count}: {entry['facility']} on {entry['date']} ({entry['hours']}h, {entry['km']}km)")
                else:
                    not_found.append(entry)
                    print(f"[NOT FOUND] {entry['facility']} on {entry['date']}")

            except Exception as e:
                print(f"[ERROR] {entry['facility']}: {e}")

    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total entries from sheet: {len(data)}")
    print(f"[OK] Updated: {updated_count} inspections")
    print(f"[NOT FOUND]: {len(not_found)} inspections")
    print(f"{'='*80}")

def main():
    """Main function"""
    # Inspector mapping: Google Sheet name -> Database inspector name
    INSPECTORS = {
        'Neo Noe': 'NEO NOE',
        'Cinga Ngongo': 'CINGA NGONGO',
        'Ben Visagie': 'BEN VISAGIE',
        'Kabelo Percy': 'PERCY MALEKA',
        'Thato Sekhotho': 'THATO SEKHOTHO',
        'Mpeluza Xola': 'XOLA MPELUZA',
        'Jofred Steyn': 'JOFRED STEYN',
        'Lwandile Maqina': 'LWANDILE MAQINA',
        'Sandisiwe Dlisani': 'SANDISIWE DLISANI',
        'Gladys Manganye': 'GLADYS MANGANYE',
        'Mokgadi Selone': 'MOKGADI SELONE',
        'Kutlwano Kuntwane': 'KUTLWANO KUNTWANE',
        'Hellen Modiba': 'HELLEN MODIBA',
        'Nelisa Ntoyaphi': 'NELISA NTOYAPHI',
        'Corneluis Adams': 'CORNELUIS ADAMS',
    }

    # Get Google Sheets service
    service = get_google_sheets_service()
    if not service:
        return

    print("="*80)
    print("GOOGLE SHEET TO DATABASE RESTORATION")
    print("Reading October-December 2025 data for all inspectors")
    print("="*80)

    total_updated = 0
    total_not_found = 0

    # Process all inspectors
    for sheet_name, db_name in INSPECTORS.items():
        print(f"\n{'='*80}")
        print(f"Processing: {sheet_name}")
        print(f"{'='*80}")

        # Extract data from sheet
        data = extract_oct_dec_data(sheet_name, service)

        # Update database
        if data:
            update_inspections(sheet_name, db_name, data)
        else:
            print(f"  No October-December 2025 data found with hours and km")

    print("\n" + "="*80)
    print("RESTORATION COMPLETE FOR ALL INSPECTORS")
    print("="*80)

if __name__ == '__main__':
    main()
