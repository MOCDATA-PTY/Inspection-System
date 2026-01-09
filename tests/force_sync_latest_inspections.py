"""
Force sync the latest inspections from SQL Server
This will pull inspections from December 25 onwards
"""
import os
import django
import sys
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
import pyodbc
from django.conf import settings

def connect_to_sql_server():
    """Connect to the remote SQL Server"""
    try:
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={settings.SQL_SERVER_HOST};"
            f"DATABASE={settings.SQL_SERVER_DATABASE};"
            f"UID={settings.SQL_SERVER_USER};"
            f"PWD={settings.SQL_SERVER_PASSWORD};"
        )
        conn = pyodbc.connect(connection_string, timeout=30)
        print("[OK] Connected to SQL Server successfully")
        return conn
    except Exception as e:
        print(f"[ERROR] Failed to connect to SQL Server: {e}")
        return None

def fetch_latest_inspections_from_commodity(cursor, commodity_table, commodity_name, start_date):
    """Fetch inspections from a specific commodity table"""
    query = f"""
    SELECT TOP 1000
        CAST([InspectionID] AS INT) as InspectionID,
        [CommodityTypeID],
        [DateOfInspection],
        [StartOfInspection],
        [EndOfInspection],
        [InspectionLocationTypeID],
        [IsDirectionPresentForThisInspection],
        [InspectorID],
        [Latitude],
        [Longitude],
        [IsSampleTaken],
        [BoughtSample],
        [InspectionTravelDistance_KM]
    FROM [{commodity_table}]
    WHERE [DateOfInspection] >= ?
    ORDER BY [DateOfInspection] DESC, [InspectionID] DESC
    """

    try:
        cursor.execute(query, start_date)
        rows = cursor.fetchall()
        print(f"  {commodity_name}: Found {len(rows)} inspections since {start_date}")
        return rows, commodity_name
    except Exception as e:
        print(f"  {commodity_name}: ERROR - {e}")
        return [], commodity_name

def main():
    print("=" * 80)
    print("FORCE SYNC LATEST INSPECTIONS FROM SQL SERVER")
    print("=" * 80)
    print()

    # Connect to SQL Server
    conn = connect_to_sql_server()
    if not conn:
        print("[ERROR] Cannot proceed without SQL Server connection")
        return

    cursor = conn.cursor()

    # Define start date (December 25, 2025)
    start_date = '2025-12-25'
    print(f"Fetching inspections from {start_date} onwards...")
    print()

    # Commodity tables mapping
    commodity_tables = {
        'PMP': 'PMP',
        'RAW': 'RAW',
        'EGGS': 'EGGS',
        'POULTRY': 'POULTRY'
    }

    all_inspections = []

    for table_name, commodity_name in commodity_tables.items():
        print(f"Checking {commodity_name} table...")
        rows, commodity = fetch_latest_inspections_from_commodity(
            cursor, table_name, commodity_name, start_date
        )

        for row in rows:
            all_inspections.append({
                'commodity': commodity,
                'remote_id': row.InspectionID,
                'date_of_inspection': row.DateOfInspection,
                'start_of_inspection': row.StartOfInspection,
                'end_of_inspection': row.EndOfInspection,
                'inspection_location_type_id': row.InspectionLocationTypeID,
                'is_direction_present': row.IsDirectionPresentForThisInspection,
                'inspector_id': row.InspectorID,
                'latitude': str(row.Latitude) if row.Latitude else None,
                'longitude': str(row.Longitude) if row.Longitude else None,
                'is_sample_taken': row.IsSampleTaken,
                'bought_sample': row.BoughtSample,
                'inspection_travel_distance_km': row.InspectionTravelDistance_KM,
            })

    print()
    print(f"Total inspections found: {len(all_inspections)}")
    print()

    if len(all_inspections) == 0:
        print("[INFO] No new inspections found after December 25, 2025")
        print("[INFO] This confirms that December 24 is indeed the latest inspection date")
        conn.close()
        return

    # Show breakdown by date
    from collections import defaultdict
    date_breakdown = defaultdict(int)
    for insp in all_inspections:
        date_breakdown[str(insp['date_of_inspection'])] += 1

    print("Breakdown by date:")
    for date in sorted(date_breakdown.keys(), reverse=True):
        print(f"  {date}: {date_breakdown[date]} inspections")
    print()

    # Ask user if they want to import
    print("=" * 80)
    print("READY TO IMPORT")
    print("=" * 80)
    print(f"Found {len(all_inspections)} inspections from SQL Server")
    print("These will be added/updated in the Django database")
    print()

    response = input("Do you want to import these inspections? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("[CANCELLED] Import cancelled by user")
        conn.close()
        return

    # Import the inspections
    print()
    print("Importing inspections...")
    imported = 0
    updated = 0
    errors = 0

    for insp_data in all_inspections:
        try:
            inspection, created = FoodSafetyAgencyInspection.objects.update_or_create(
                commodity=insp_data['commodity'],
                remote_id=insp_data['remote_id'],
                defaults={
                    'date_of_inspection': insp_data['date_of_inspection'],
                    'start_of_inspection': insp_data['start_of_inspection'],
                    'end_of_inspection': insp_data['end_of_inspection'],
                    'inspection_location_type_id': insp_data['inspection_location_type_id'],
                    'is_direction_present_for_this_inspection': insp_data['is_direction_present'],
                    'inspector_id': insp_data['inspector_id'],
                    'latitude': insp_data['latitude'],
                    'longitude': insp_data['longitude'],
                    'is_sample_taken': insp_data['is_sample_taken'],
                    'bought_sample': insp_data['bought_sample'],
                    'inspection_travel_distance_km': insp_data['inspection_travel_distance_km'],
                }
            )

            if created:
                imported += 1
            else:
                updated += 1

        except Exception as e:
            errors += 1
            print(f"[ERROR] Failed to import {insp_data['commodity']}-{insp_data['remote_id']}: {e}")

    print()
    print("=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"New inspections imported: {imported}")
    print(f"Existing inspections updated: {updated}")
    print(f"Errors: {errors}")
    print()

    # Show latest inspection after import
    if imported > 0 or updated > 0:
        latest = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection', '-created_at').first()
        print(f"Latest inspection in database now:")
        print(f"  ID: {latest.unique_inspection_id}")
        print(f"  Date: {latest.date_of_inspection}")
        print(f"  Inspector: {latest.inspector_name}")
        print(f"  Client: {latest.client_name}")

    conn.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
