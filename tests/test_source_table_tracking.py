"""
Diagnostic test to track which source table each inspection comes from
and identify if duplicates are from server or system
"""
import pymssql
from datetime import datetime

# SQL Server connection details
SQLSERVER_CONFIG = {
    'server': '102.67.140.12',
    'port': 1053,
    'user': 'FSAUser2',
    'password': 'password',
    'database': 'AFS',
    'timeout': 30
}

def test_source_table_tracking():
    """Test to identify source tables and track duplicates"""

    print("=" * 80)
    print("SOURCE TABLE TRACKING & DUPLICATE DIAGNOSTIC")
    print("=" * 80)
    print()

    try:
        # Connect to SQL Server
        print("Connecting to SQL Server...")
        connection = pymssql.connect(
            server=SQLSERVER_CONFIG['server'],
            port=SQLSERVER_CONFIG['port'],
            user=SQLSERVER_CONFIG['user'],
            password=SQLSERVER_CONFIG['password'],
            database=SQLSERVER_CONFIG['database'],
            timeout=SQLSERVER_CONFIG['timeout']
        )
        print("[OK] Connected successfully")
        print()

        cursor = connection.cursor()

        # TEST 1: Check Chubby Chick 1 inspections (342, 343, 344, 436)
        print("=" * 80)
        print("TEST CASE: Chubby Chick 1 - Inspections 342, 343, 344, 436")
        print("=" * 80)
        print()

        inspection_ids = [342, 343, 344, 436]

        # Check each poultry source table
        print("STEP 1: Checking PoultryQuidInspectionRecordTypes")
        print("-" * 80)

        query_quid = """
        SELECT
            'PoultryQuidInspectionRecordTypes' as SourceTable,
            Id as InspectionId,
            DateOfInspection,
            InspectorId,
            CreatedOn,
            ModifiedOn,
            ProductName,
            IsActive
        FROM AFS.dbo.PoultryQuidInspectionRecordTypes
        WHERE Id IN (342, 343, 344, 436)
        ORDER BY Id
        """

        cursor.execute(query_quid)
        columns = [col[0] for col in cursor.description]
        quid_rows = cursor.fetchall()

        if quid_rows:
            print(f"Found {len(quid_rows)} records in PoultryQuidInspectionRecordTypes:")
            for row in quid_rows:
                rec = dict(zip(columns, row))
                print(f"  ID {rec['InspectionId']}: {rec['ProductName']} (Created: {rec['CreatedOn']})")
        else:
            print("No records found in PoultryQuidInspectionRecordTypes")

        print()

        # Check PoultryGradingInspectionRecordTypes
        print("STEP 2: Checking PoultryGradingInspectionRecordTypes")
        print("-" * 80)

        query_grading = """
        SELECT
            'PoultryGradingInspectionRecordTypes' as SourceTable,
            Id as InspectionId,
            DateOfInspection,
            InspectorId,
            CreatedOn,
            ModifiedOn,
            ProductName,
            IsActive
        FROM AFS.dbo.PoultryGradingInspectionRecordTypes
        WHERE Id IN (342, 343, 344, 436)
        ORDER BY Id
        """

        cursor.execute(query_grading)
        columns = [col[0] for col in cursor.description]
        grading_rows = cursor.fetchall()

        if grading_rows:
            print(f"Found {len(grading_rows)} records in PoultryGradingInspectionRecordTypes:")
            for row in grading_rows:
                rec = dict(zip(columns, row))
                print(f"  ID {rec['InspectionId']}: {rec['ProductName']} (Created: {rec['CreatedOn']})")
        else:
            print("No records found in PoultryGradingInspectionRecordTypes")

        print()

        # Check PoultryLabelInspectionChecklistRecords
        print("STEP 3: Checking PoultryLabelInspectionChecklistRecords")
        print("-" * 80)

        query_label = """
        SELECT
            'PoultryLabelInspectionChecklistRecords' as SourceTable,
            Id as InspectionId,
            DateOfInspection,
            InspectorId,
            CreatedOn,
            ModifiedOn,
            ProductName,
            IsActive
        FROM AFS.dbo.PoultryLabelInspectionChecklistRecords
        WHERE Id IN (342, 343, 344, 436)
        ORDER BY Id
        """

        cursor.execute(query_label)
        columns = [col[0] for col in cursor.description]
        label_rows = cursor.fetchall()

        if label_rows:
            print(f"Found {len(label_rows)} records in PoultryLabelInspectionChecklistRecords:")
            for row in label_rows:
                rec = dict(zip(columns, row))
                print(f"  ID {rec['InspectionId']}: {rec['ProductName']} (Created: {rec['CreatedOn']})")
        else:
            print("No records found in PoultryLabelInspectionChecklistRecords")

        print()

        # Detailed analysis of found records
        print("=" * 80)
        print("DETAILED ANALYSIS")
        print("=" * 80)
        print()

        all_records = []

        for row in quid_rows:
            rec = dict(zip(columns, row))
            all_records.append(rec)

        for row in grading_rows:
            rec = dict(zip(columns, row))
            all_records.append(rec)

        for row in label_rows:
            rec = dict(zip(columns, row))
            all_records.append(rec)

        if all_records:
            # Sort by inspection ID
            all_records.sort(key=lambda x: x['InspectionId'])

            for rec in all_records:
                print(f"Inspection {rec['InspectionId']}:")
                print(f"  Source Table: {rec['SourceTable']}")
                print(f"  Product: {rec['ProductName']}")
                print(f"  Date: {rec['DateOfInspection']}")
                print(f"  Inspector ID: {rec['InspectorId']}")
                print(f"  Created On: {rec['CreatedOn']}")
                print(f"  Modified On: {rec['ModifiedOn']}")
                print(f"  Is Active: {rec['IsActive']}")
                print()

            # Check for duplicates
            print("DUPLICATE DETECTION:")
            print("-" * 80)

            # Group by product name
            from collections import defaultdict
            product_groups = defaultdict(list)

            for rec in all_records:
                # Normalize product name for comparison
                product_key = (
                    rec['ProductName'].strip().lower() if rec['ProductName'] else '',
                    rec['DateOfInspection'].strftime('%Y-%m-%d') if rec['DateOfInspection'] else '',
                    rec['InspectorId']
                )
                product_groups[product_key].append(rec)

            # Find duplicates
            duplicates_found = False
            for key, records in product_groups.items():
                if len(records) > 1:
                    duplicates_found = True
                    product_name, date, inspector = key
                    print(f"[DUPLICATE] Product '{product_name}' on {date} by inspector {inspector}:")
                    for rec in records:
                        time_diff = ""
                        if len(records) > 1:
                            first_created = records[0]['CreatedOn']
                            time_delta = (rec['CreatedOn'] - first_created).total_seconds()
                            time_diff = f" (+{time_delta:.0f}s from first)"

                        print(f"  - Inspection {rec['InspectionId']} from {rec['SourceTable']}")
                        print(f"    Created: {rec['CreatedOn']}{time_diff}")
                    print()

            if not duplicates_found:
                print("[OK] No duplicates detected within these inspections")

        else:
            print("[ERROR] No records found for these inspection IDs")
            print("These IDs may not exist in any poultry table")

        print()

        # TEST 2: Check for other clients with duplicates
        print("=" * 80)
        print("SCANNING FOR OTHER DUPLICATES (Recent data)")
        print("=" * 80)
        print()

        # Query to find all recent duplicates across all poultry tables
        duplicate_scan_query = """
        WITH AllPoultryInspections AS (
            SELECT
                'PoultryQuidInspectionRecordTypes' as SourceTable,
                Id as InspectionId,
                DateOfInspection,
                InspectorId,
                CreatedOn,
                ProductName,
                ClientId
            FROM AFS.dbo.PoultryQuidInspectionRecordTypes
            WHERE IsActive = 1
            AND DateOfInspection >= '2025-12-01'
            AND DateOfInspection < '2025-12-04'
            AND ProductName IS NOT NULL
            AND ProductName != ''

            UNION ALL

            SELECT
                'PoultryGradingInspectionRecordTypes' as SourceTable,
                Id as InspectionId,
                DateOfInspection,
                InspectorId,
                CreatedOn,
                ProductName,
                ClientId
            FROM AFS.dbo.PoultryGradingInspectionRecordTypes
            WHERE IsActive = 1
            AND DateOfInspection >= '2025-12-01'
            AND DateOfInspection < '2025-12-04'
            AND ProductName IS NOT NULL
            AND ProductName != ''

            UNION ALL

            SELECT
                'PoultryLabelInspectionChecklistRecords' as SourceTable,
                Id as InspectionId,
                DateOfInspection,
                InspectorId,
                CreatedOn,
                ProductName,
                ClientId
            FROM AFS.dbo.PoultryLabelInspectionChecklistRecords
            WHERE IsActive = 1
            AND DateOfInspection >= '2025-12-01'
            AND DateOfInspection < '2025-12-04'
            AND ProductName IS NOT NULL
            AND ProductName != ''
        )
        SELECT
            DateOfInspection,
            InspectorId,
            ClientId,
            ProductName,
            COUNT(*) as InspectionCount,
            STRING_AGG(CAST(InspectionId as VARCHAR), ', ') as InspectionIds,
            STRING_AGG(SourceTable, ', ') as SourceTables
        FROM AllPoultryInspections
        GROUP BY DateOfInspection, InspectorId, ClientId, ProductName
        HAVING COUNT(*) > 1
        ORDER BY DateOfInspection DESC, InspectionCount DESC
        """

        cursor.execute(duplicate_scan_query)
        columns = [col[0] for col in cursor.description]
        duplicate_rows = cursor.fetchall()

        if duplicate_rows:
            print(f"Found {len(duplicate_rows)} potential duplicate groups:")
            print()

            for row in duplicate_rows:
                rec = dict(zip(columns, row))
                print(f"Date: {rec['DateOfInspection']}, Inspector: {rec['InspectorId']}, Client: {rec['ClientId']}")
                print(f"  Product: {rec['ProductName']}")
                print(f"  Count: {rec['InspectionCount']} inspections")
                print(f"  IDs: {rec['InspectionIds']}")
                print(f"  Source Tables: {rec['SourceTables']}")
                print()
        else:
            print("[OK] No recent poultry duplicates found")

        print()
        print("=" * 80)
        print("DIAGNOSIS COMPLETE")
        print("=" * 80)

        cursor.close()
        connection.close()

        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_source_table_tracking()
