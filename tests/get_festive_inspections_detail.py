#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get detailed information for specific Festive inspections
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

from main.models import FoodSafetyAgencyInspection

def get_inspection_details():
    """Get detailed information for specific inspections"""

    print(f"\n{'='*120}")
    print(f"FESTIVE INSPECTIONS - DETAILED REPORT")
    print(f"Date: November 17, 2025")
    print(f"{'='*120}\n")

    # The inspection IDs from the user's table
    inspection_ids = [324, 424, 6329, 6330, 6343]

    inspections = FoodSafetyAgencyInspection.objects.filter(
        remote_id__in=inspection_ids
    ).order_by('remote_id')

    print(f"Found {inspections.count()} inspections\n")

    for idx, insp in enumerate(inspections, 1):
        print(f"{'='*120}")
        print(f"INSPECTION #{idx}: Remote ID {insp.remote_id}")
        print(f"{'='*120}\n")

        # Basic Information
        print(f"📋 BASIC INFORMATION:")
        print(f"   Client Name: {insp.client_name}")
        print(f"   Account Code: {insp.internal_account_code}")
        print(f"   Commodity: {insp.commodity}")
        print(f"   Product: {insp.product_name}")
        print()

        # Date and Time
        print(f"📅 DATE & TIME:")
        print(f"   Inspection Date: {insp.date_of_inspection}")
        print(f"   Start Time: {insp.start_of_inspection}")
        print(f"   End Time: {insp.end_of_inspection}")
        if insp.start_of_inspection and insp.end_of_inspection:
            try:
                from datetime import datetime, timedelta
                # Convert time to datetime for duration calculation
                start_dt = datetime.combine(insp.date_of_inspection, insp.start_of_inspection)
                end_dt = datetime.combine(insp.date_of_inspection, insp.end_of_inspection)
                duration = end_dt - start_dt
                minutes = duration.total_seconds() / 60
                print(f"   Duration: {int(minutes)} minutes")
            except:
                pass
        print()

        # Inspector Information
        print(f"👤 INSPECTOR:")
        print(f"   Name: {insp.inspector_name}")
        print(f"   ID: {insp.inspector_id}")
        print()

        # Location Information
        print(f"📍 LOCATION:")
        print(f"   Latitude: {insp.latitude}")
        print(f"   Longitude: {insp.longitude}")
        print(f"   Location Type ID: {insp.inspection_location_type_id}")
        print(f"   Direction Present: {insp.is_direction_present_for_this_inspection}")
        if insp.latitude and insp.longitude:
            print(f"   Google Maps: https://www.google.com/maps?q={insp.latitude},{insp.longitude}")
        print()

        # Inspection Details
        print(f"🔍 INSPECTION DETAILS:")
        print(f"   Sample Taken: {insp.is_sample_taken}")
        print(f"   KM Traveled: {insp.km_traveled if insp.km_traveled else 'Not recorded'}")
        print(f"   Hours: {insp.hours if insp.hours else 'Not recorded'}")
        print()

        # Status Information
        print(f"📊 STATUS:")
        print(f"   Is Sent: {insp.is_sent}")
        if insp.is_sent:
            print(f"   Sent Date: {insp.sent_date}")
            if insp.sent_by:
                print(f"   Sent By: {insp.sent_by.username}")
        print(f"   OneDrive Uploaded: {insp.onedrive_uploaded}")
        if insp.onedrive_uploaded:
            print(f"   OneDrive Upload Date: {insp.onedrive_upload_date}")
            print(f"   OneDrive Folder ID: {insp.onedrive_folder_id}")
        print()

        # Database Information
        print(f"💾 DATABASE:")
        print(f"   Django ID: {insp.id}")
        print(f"   Remote ID: {insp.remote_id}")
        print(f"   Created: {insp.created_at}")
        print(f"   Updated: {insp.updated_at}")
        print()

    # Summary Analysis
    print(f"\n{'='*120}")
    print(f"ANALYSIS SUMMARY")
    print(f"{'='*120}\n")

    # Check if all from same client and account
    unique_clients = inspections.values_list('client_name', flat=True).distinct()
    unique_accounts = inspections.values_list('internal_account_code', flat=True).distinct()
    unique_commodities = inspections.values_list('commodity', flat=True).distinct()
    unique_inspectors = inspections.values_list('inspector_name', flat=True).distinct()

    print(f"📊 UNIQUE VALUES:")
    print(f"   Clients: {list(unique_clients)}")
    print(f"   Account Codes: {list(unique_accounts)}")
    print(f"   Commodities: {list(unique_commodities)}")
    print(f"   Inspectors: {list(unique_inspectors)}")
    print()

    # Products breakdown
    print(f"🥩 PRODUCTS INSPECTED:")
    for insp in inspections:
        print(f"   - {insp.product_name}")
    print()

    # Location clustering (check if all at same location)
    print(f"📍 LOCATION ANALYSIS:")
    locations = inspections.values_list('latitude', 'longitude').distinct()
    print(f"   Unique Locations: {len(locations)}")
    for lat, lng in locations:
        count = inspections.filter(latitude=lat, longitude=lng).count()
        print(f"   - {lat}, {lng} ({count} inspections)")
    print()

    # Commodity Mismatch Check
    print(f"⚠️  COMMODITY MISMATCH CHECK:")
    for account in unique_accounts:
        if account:
            account_upper = account.upper()
            if 'RAW' in account_upper:
                expected = 'RAW'
            elif 'PMP' in account_upper or 'PROCESSED' in account_upper:
                expected = 'PMP'
            elif 'POULTRY' in account_upper or 'PTY' in account_upper:
                expected = 'POULTRY'
            elif 'EGG' in account_upper:
                expected = 'EGGS'
            else:
                expected = 'Unknown'

            actual = list(unique_commodities)

            print(f"   Account Code: {account}")
            print(f"   Expected Commodity (from account code): {expected}")
            print(f"   Actual Commodity (from inspections): {actual}")

            if expected in actual and len(actual) == 1:
                print(f"   Status: ✅ MATCH")
            else:
                print(f"   Status: ❌ MISMATCH - Account says {expected}, but inspections show {actual}")
                print(f"   Action: Review SQL Server data - either account code or commodity assignment is incorrect")

    print(f"\n{'='*120}\n")


if __name__ == "__main__":
    try:
        get_inspection_details()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
