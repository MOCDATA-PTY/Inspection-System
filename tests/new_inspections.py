#!/usr/bin/env python
"""
Script to fetch all inspections with client names containing "New"
Displays: Remote ID (SQL Server), Client Name, Inspection Date, Account Code, and Commodity
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

def main():
    print("=" * 110)
    print("ALL 'NEW' CLIENT INSPECTIONS - FROM THE BEGINNING OF TIME")
    print("=" * 110)
    print(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Query ALL inspections with client names containing "New" (case-insensitive)
    # IMPORTANT: Using RAW SQL to bypass ALL Django ORM filters and managers
    # This pulls data from the BEGINNING OF TIME - no date restrictions!
    from django.db import connection

    # Use raw SQL to get absolutely everything from the database
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, remote_id, client_name, date_of_inspection,
                   internal_account_code, commodity
            FROM food_safety_agency_inspections
            WHERE LOWER(client_name) LIKE LOWER(%s)
            ORDER BY date_of_inspection DESC, client_name
        """, ['%New%'])

        raw_results = cursor.fetchall()

    # Convert raw results to a list of dictionaries for easier handling
    inspection_data = []
    for row in raw_results:
        inspection_data.append({
            'id': row[0],
            'remote_id': row[1],
            'client_name': row[2],
            'date_of_inspection': row[3],
            'internal_account_code': row[4],
            'commodity': row[5]
        })

    total_count = len(inspection_data)
    print(f"Total Inspections Found (RAW SQL - ALL TIME): {total_count}")

    # Show date range to verify we're pulling from the beginning of time
    if total_count > 0:
        dates = [row['date_of_inspection'] for row in inspection_data if row['date_of_inspection']]
        if dates:
            earliest = min(dates)
            latest = max(dates)
            if isinstance(earliest, str):
                print(f"Date Range: {earliest} to {latest}")
            else:
                print(f"Date Range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}")
    print()

    if total_count == 0:
        print("No inspections found with client names containing 'New'.")
        return

    # Print table header
    print(f"{'#':<6} {'Remote ID':<12} {'Client Name':<35} {'Inspection Date':<18} {'Account Code':<20} {'Commodity':<15}")
    print("-" * 110)

    # Print each inspection
    for index, inspection in enumerate(inspection_data, 1):
        remote_id = str(inspection['remote_id']) if inspection['remote_id'] else "N/A"
        client_name = inspection['client_name'] or "N/A"

        # Handle date formatting (could be date object or string)
        date_val = inspection['date_of_inspection']
        if date_val:
            if isinstance(date_val, str):
                inspection_date = date_val
            else:
                inspection_date = date_val.strftime('%Y-%m-%d')
        else:
            inspection_date = "N/A"

        account_code = inspection['internal_account_code'] or "N/A"
        commodity = inspection['commodity'] or "N/A"

        # Truncate long client names to fit the table
        if len(client_name) > 34:
            client_name = client_name[:31] + "..."

        print(f"{index:<6} {remote_id:<12} {client_name:<35} {inspection_date:<18} {account_code:<20} {commodity:<15}")

    print("-" * 110)
    print(f"\nTotal: {total_count} inspections\n")

    # Summary statistics
    print("\n" + "=" * 110)
    print("SUMMARY STATISTICS")
    print("=" * 110)

    # Count by commodity
    from collections import Counter
    commodity_list = [row['commodity'] or "Not Specified" for row in inspection_data]
    commodity_counts = Counter(commodity_list)
    print("\nInspections by Commodity:")
    for commodity_name, count in commodity_counts.most_common():
        print(f"  {commodity_name}: {count}")

    # Date range
    dates = [row['date_of_inspection'] for row in inspection_data if row['date_of_inspection']]
    if dates:
        earliest = min(dates)
        latest = max(dates)
        print(f"\nDate Range:")
        if isinstance(earliest, str):
            print(f"  Earliest: {earliest}")
            print(f"  Latest: {latest}")
        else:
            print(f"  Earliest: {earliest.strftime('%Y-%m-%d')}")
            print(f"  Latest: {latest.strftime('%Y-%m-%d')}")

    print("\n" + "=" * 110)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
