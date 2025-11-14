#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to diagnose inspection sync issues
This script tests the SQL Server connection and sync functionality
"""
import os
import sys
import django
from datetime import datetime

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection
from main.views.data_views import FSA_INSPECTION_QUERY, INSPECTOR_NAME_MAP

def test_sql_connection():
    """Test SQL Server connection"""
    print("\n" + "="*80)
    print("STEP 1: TESTING SQL SERVER CONNECTION")
    print("="*80)

    try:
        import pymssql
        print("✓ pymssql module imported successfully")

        # Get SQL Server configuration
        sql_server_config = settings.DATABASES.get('sql_server', {})
        print(f"\nConnection details:")
        print(f"  Host: {sql_server_config.get('HOST')}")
        print(f"  Port: {sql_server_config.get('PORT')}")
        print(f"  Database: {sql_server_config.get('NAME')}")
        print(f"  User: {sql_server_config.get('USER')}")

        # Attempt connection
        print("\nAttempting to connect to SQL Server...")
        connection = pymssql.connect(
            server=sql_server_config.get('HOST'),
            port=int(sql_server_config.get('PORT', 1433)),
            user=sql_server_config.get('USER'),
            password=sql_server_config.get('PASSWORD'),
            database=sql_server_config.get('NAME'),
            timeout=30
        )
        print("✓ Successfully connected to SQL Server!")

        cursor = connection.cursor(as_dict=True)
        print("✓ Cursor created successfully")

        return connection, cursor

    except ImportError as e:
        print(f"✗ ERROR: pymssql not installed - {e}")
        return None, None
    except Exception as e:
        print(f"✗ ERROR: Connection failed - {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_query_execution(cursor):
    """Test executing the FSA inspection query"""
    print("\n" + "="*80)
    print("STEP 2: TESTING QUERY EXECUTION")
    print("="*80)

    if not cursor:
        print("✗ Skipping - no cursor available")
        return None

    try:
        print("\nExecuting FSA_INSPECTION_QUERY...")
        print(f"Query length: {len(FSA_INSPECTION_QUERY)} characters")

        # Show first 500 chars of query
        print(f"\nQuery preview (first 500 chars):")
        print("-" * 80)
        print(FSA_INSPECTION_QUERY[:500])
        print("...")
        print("-" * 80)

        cursor.execute(FSA_INSPECTION_QUERY)
        print("✓ Query executed successfully!")

        # Fetch all results
        print("\nFetching results...")
        rows = cursor.fetchall()
        print(f"✓ Fetched {len(rows)} inspection records")

        return rows

    except Exception as e:
        print(f"✗ ERROR: Query execution failed - {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_results(rows):
    """Analyze the query results"""
    print("\n" + "="*80)
    print("STEP 3: ANALYZING QUERY RESULTS")
    print("="*80)

    if not rows:
        print("✗ No rows returned from query")
        print("\nPossible reasons:")
        print("  1. No inspections exist in the database for the date range (>= 2025-10-01)")
        print("  2. The query filters are too restrictive")
        print("  3. Data exists but doesn't meet the query criteria")
        return

    print(f"\n✓ Total inspections: {len(rows)}")

    # Analyze by commodity
    commodities = {}
    for row in rows:
        commodity = row.get('Commodity', 'Unknown')
        commodities[commodity] = commodities.get(commodity, 0) + 1

    print("\nBreakdown by Commodity:")
    for commodity, count in sorted(commodities.items()):
        print(f"  {commodity}: {count}")

    # Analyze by date
    dates = {}
    for row in rows:
        date = row.get('DateOfInspection')
        if date:
            date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
            dates[date_str] = dates.get(date_str, 0) + 1

    print("\nBreakdown by Date (most recent 10):")
    for date_str, count in sorted(dates.items(), reverse=True)[:10]:
        print(f"  {date_str}: {count}")

    # Analyze by inspector
    inspectors = {}
    for row in rows:
        inspector_id = row.get('InspectorId')
        try:
            inspector_id_int = int(inspector_id) if inspector_id is not None else None
        except (TypeError, ValueError):
            inspector_id_int = None

        inspector_name = INSPECTOR_NAME_MAP.get(inspector_id_int, f'Unknown ({inspector_id})')
        inspectors[inspector_name] = inspectors.get(inspector_name, 0) + 1

    print("\nBreakdown by Inspector (top 10):")
    for inspector, count in sorted(inspectors.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {inspector}: {count}")

    # Show sample records
    print("\nSample Records (first 3):")
    for i, row in enumerate(rows[:3], 1):
        print(f"\n  Record {i}:")
        print(f"    ID: {row.get('Id')}")
        print(f"    Commodity: {row.get('Commodity')}")
        print(f"    Client: {row.get('Client')}")
        print(f"    Date: {row.get('DateOfInspection')}")
        print(f"    Inspector ID: {row.get('InspectorId')}")
        print(f"    Product Name: {row.get('ProductName', 'N/A')}")

def test_database_sync(rows):
    """Test syncing to the database"""
    print("\n" + "="*80)
    print("STEP 4: TESTING DATABASE SYNC")
    print("="*80)

    if not rows:
        print("✗ Skipping - no rows to sync")
        return

    try:
        # Check existing count
        existing_count = FoodSafetyAgencyInspection.objects.count()
        print(f"\nExisting inspections in database: {existing_count}")

        # Test creating one inspection
        print("\nTesting creation of a single inspection...")
        row = rows[0]

        inspector_id = row.get('InspectorId')
        try:
            inspector_id_int = int(inspector_id) if inspector_id is not None else None
        except (TypeError, ValueError):
            inspector_id_int = None

        inspector_name = INSPECTOR_NAME_MAP.get(inspector_id_int, 'Unknown')

        test_inspection = FoodSafetyAgencyInspection(
            commodity=row.get('Commodity'),
            date_of_inspection=row.get('DateOfInspection'),
            start_of_inspection=row.get('StartOfInspection'),
            end_of_inspection=row.get('EndOfInspection'),
            inspection_location_type_id=row.get('InspectionLocationTypeID'),
            is_direction_present_for_this_inspection=row.get('IsDirectionPresentForthisInspection', False),
            inspector_id=inspector_id_int,
            inspector_name=inspector_name,
            latitude=row.get('Latitude'),
            longitude=row.get('Longitude'),
            is_sample_taken=row.get('IsSampleTaken', False),
            remote_id=row.get('Id'),
            client_name=row.get('Client'),
            product_name=row.get('ProductName')
        )

        # Don't actually save, just validate
        test_inspection.full_clean()
        print("✓ Test inspection validated successfully")
        print(f"  Details: {test_inspection.client_name} - {test_inspection.commodity}")

    except Exception as e:
        print(f"✗ ERROR: Failed to create test inspection - {e}")
        import traceback
        traceback.print_exc()

def run_full_sync_test():
    """Run the full sync process"""
    print("\n" + "="*80)
    print("STEP 5: RUNNING FULL SYNC (using populate_inspections_table)")
    print("="*80)

    try:
        from main.services.google_sheets_service import GoogleSheetsService

        print("\nInitializing GoogleSheetsService...")
        sheets_service = GoogleSheetsService()

        print("Running populate_inspections_table...")
        result = sheets_service.populate_inspections_table()

        print("\nSync Result:")
        print(f"  Success: {result.get('success')}")
        print(f"  Deleted: {result.get('deleted_count', 0)}")
        print(f"  Created: {result.get('inspections_created', 0)}")
        print(f"  Processed: {result.get('total_processed', 0)}")

        if not result.get('success'):
            print(f"  Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"✗ ERROR: Full sync failed - {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("FOOD SAFETY AGENCY INSPECTION SYNC DIAGNOSTIC TEST")
    print("="*80)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Test connection
    connection, cursor = test_sql_connection()

    if not connection or not cursor:
        print("\n" + "="*80)
        print("DIAGNOSTIC COMPLETE - CONNECTION FAILED")
        print("="*80)
        print("\nThe sync is failing because the SQL Server connection cannot be established.")
        print("Please check:")
        print("  1. Network connectivity to 102.67.140.12:1053")
        print("  2. SQL Server credentials (FSAUser2 / password)")
        print("  3. Firewall settings")
        print("  4. SQL Server is running and accepting connections")
        return

    # Step 2: Test query
    rows = test_query_execution(cursor)

    # Step 3: Analyze results
    analyze_results(rows)

    # Step 4: Test database operations
    test_database_sync(rows)

    # Close connection
    cursor.close()
    connection.close()
    print("\n✓ SQL Server connection closed")

    # Step 5: Run full sync
    run_full_sync_test()

    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
