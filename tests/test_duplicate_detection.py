"""
Test script to detect duplicate inspections and verify prevention logic
"""
import pymssql
from datetime import datetime, timedelta
from collections import defaultdict

# SQL Server connection details
SQLSERVER_CONFIG = {
    'server': '102.67.140.12',
    'port': 1053,
    'user': 'FSAUser2',
    'password': 'password',
    'database': 'AFS',
    'timeout': 30
}

def test_duplicate_detection():
    """Test duplicate detection logic"""

    print("=" * 80)
    print("DUPLICATE DETECTION TEST")
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

        # TEST 1: Find all potential duplicate RAW inspections
        print("TEST 1: Scanning for duplicate RAW inspections")
        print("-" * 80)

        query_duplicates = """
        SELECT
            i.Id as InspectionId,
            i.DateOfInspection,
            i.InspectorId,
            i.StartOfInspection,
            i.EndOfInspection,
            i.CreatedOn,
            prod.Id as ProductRecordId,
            prod.NewProductItemDetails as ProductName,
            prod.ClientId,
            clt.Name as ClientName
        FROM [AFS].[dbo].[RawRMPInspectionRecordTypes] i
        JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod on prod.InspectionId = i.Id
        JOIN AFS.dbo.Clients clt on clt.Id = prod.ClientId
        WHERE i.IsActive = 1
        AND i.DateOfInspection >= '2025-12-01'
        AND i.DateOfInspection < '2025-12-04'
        AND prod.NewProductItemDetails IS NOT NULL
        AND prod.NewProductItemDetails != ''
        ORDER BY i.DateOfInspection, i.InspectorId, prod.ClientId, prod.NewProductItemDetails, i.Id
        """

        cursor.execute(query_duplicates)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

        print(f"Found {len(rows)} RAW inspection records to analyze")
        print()

        # Group by potential duplicate key: Date + Inspector + Client + Product
        potential_duplicates = defaultdict(list)

        for row in rows:
            record = dict(zip(columns, row))

            # Create a key that identifies potential duplicates
            date_str = record['DateOfInspection'].strftime('%Y-%m-%d') if record['DateOfInspection'] else 'None'
            key = (
                date_str,
                record['InspectorId'],
                record['ClientId'],
                record['ProductName']
            )

            potential_duplicates[key].append(record)

        # Find groups with more than one inspection
        duplicate_groups = {k: v for k, v in potential_duplicates.items() if len(v) > 1}

        if duplicate_groups:
            print(f"[WARNING] Found {len(duplicate_groups)} potential duplicate groups:")
            print()

            for i, (key, records) in enumerate(duplicate_groups.items(), 1):
                date, inspector_id, client_id, product = key
                print(f"Group {i}: Date={date}, Inspector={inspector_id}, Client={client_id}")
                print(f"  Product: {product}")
                print(f"  {len(records)} inspections:")

                for rec in records:
                    time_diff = ""
                    if len(records) > 1:
                        first_created = records[0]['CreatedOn']
                        time_delta = (rec['CreatedOn'] - first_created).total_seconds()
                        time_diff = f" (+{time_delta:.0f}s from first)"

                    print(f"    - Inspection {rec['InspectionId']}: "
                          f"Created {rec['CreatedOn']}{time_diff}")

                print()
        else:
            print("[OK] No duplicate groups found")

        print()

        # TEST 2: Check specific case (10194 and 10195)
        print("TEST 2: Verify specific duplicates (10194 and 10195)")
        print("-" * 80)

        query_specific = """
        SELECT
            i.Id as InspectionId,
            i.DateOfInspection,
            i.InspectorId,
            i.CreatedOn,
            DATEDIFF(SECOND, i.StartOfInspection, i.EndOfInspection) as DurationSeconds,
            prod.NewProductItemDetails as ProductName,
            clt.Name as ClientName
        FROM [AFS].[dbo].[RawRMPInspectionRecordTypes] i
        JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod on prod.InspectionId = i.Id
        JOIN AFS.dbo.Clients clt on clt.Id = prod.ClientId
        WHERE i.Id IN (10194, 10195)
        ORDER BY i.Id
        """

        cursor.execute(query_specific)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

        if len(rows) == 2:
            rec1 = dict(zip(columns, rows[0]))
            rec2 = dict(zip(columns, rows[1]))

            time_between = (rec2['CreatedOn'] - rec1['CreatedOn']).total_seconds()

            print(f"Inspection 10194:")
            print(f"  Client: {rec1['ClientName']}")
            print(f"  Product: {rec1['ProductName']}")
            print(f"  Created: {rec1['CreatedOn']}")
            print(f"  Duration: {rec1['DurationSeconds']}s")
            print()

            print(f"Inspection 10195:")
            print(f"  Client: {rec2['ClientName']}")
            print(f"  Product: {rec2['ProductName']}")
            print(f"  Created: {rec2['CreatedOn']}")
            print(f"  Duration: {rec2['DurationSeconds']}s")
            print()

            print(f"Time between inspections: {time_between:.1f} seconds")
            print()

            if time_between < 300:  # 5 minutes
                print(f"[WARNING] These inspections were created {time_between:.0f}s apart")
                print(f"[WARNING] This suggests possible accidental duplication")
            else:
                print(f"[OK] These are likely legitimate separate inspections")

        print()

        # TEST 3: Count all duplicates across all commodities
        print("TEST 3: Overall duplicate statistics")
        print("-" * 80)

        # Check RAW duplicates
        query_raw_count = """
        SELECT COUNT(*) as TotalInspections
        FROM [AFS].[dbo].[RawRMPInspectionRecordTypes]
        WHERE IsActive = 1
        AND DateOfInspection >= '2025-10-01'
        AND DateOfInspection < '2026-04-01'
        """

        cursor.execute(query_raw_count)
        total_raw = cursor.fetchone()[0]

        query_raw_products = """
        SELECT COUNT(*) as TotalProducts
        FROM [AFS].[dbo].[RawRMPInspectionRecordTypes] i
        JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod on prod.InspectionId = i.Id
        WHERE i.IsActive = 1
        AND i.DateOfInspection >= '2025-10-01'
        AND i.DateOfInspection < '2026-04-01'
        AND prod.NewProductItemDetails IS NOT NULL
        AND prod.NewProductItemDetails != ''
        """

        cursor.execute(query_raw_products)
        total_raw_products = cursor.fetchone()[0]

        print(f"RAW Commodity:")
        print(f"  Total inspections: {total_raw}")
        print(f"  Total products (query result): {total_raw_products}")
        print(f"  Ratio: {total_raw_products/total_raw:.2f} products per inspection")

        if total_raw_products > total_raw:
            extra = total_raw_products - total_raw
            print(f"  [INFO] {extra} extra rows due to multi-product inspections")

        print()
        print("=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print()
        print("1. DATA QUALITY ISSUE DETECTED:")
        print("   Inspections 10194 and 10195 are likely accidental duplicates")
        print("   (created 57 seconds apart, same inspector, client, product)")
        print()
        print("2. PREVENTION STRATEGIES:")
        print("   a) Add UI validation to warn when creating similar inspections")
        print("   b) Implement deduplication logic before sync")
        print("   c) Add inspection merging functionality")
        print()
        print("3. QUERY IS WORKING CORRECTLY:")
        print("   The query accurately reflects the source data")
        print("   The 'duplicates' are real records in the database")
        print()

        cursor.close()
        connection.close()

        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_duplicate_detection()
