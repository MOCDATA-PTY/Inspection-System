"""
Test script to verify POULTRY commodity name change works correctly
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

# Updated query with POULTRY instead of POULTRY_LABEL
FSA_INSPECTION_QUERY = '''
    SELECT 'POULTRY_QUID' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PoultryQuidInspectionRecordTypes].Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber, [AFS].[dbo].[PoultryQuidInspectionRecordTypes].ProductName as ProductName FROM AFS.dbo.PoultryQuidInspectionRecordTypes OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM AFS.dbo.GPSInspectionLocationRecords WHERE PoultryQuidInspectionRecordId = [AFS].[dbo].PoultryQuidInspectionRecordTypes.Id ORDER BY Id) gps join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].PoultryQuidInspectionRecordTypes.ClientId where AFS.dbo.PoultryQuidInspectionRecordTypes.IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01' AND [AFS].[dbo].[PoultryQuidInspectionRecordTypes].ProductName IS NOT NULL AND [AFS].[dbo].[PoultryQuidInspectionRecordTypes].ProductName != ''
    UNION ALL
    SELECT 'POULTRY_GRADING' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PoultryGradingInspectionRecordTypes].Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber, [AFS].[dbo].[PoultryGradingInspectionRecordTypes].ProductName as ProductName FROM AFS.dbo.PoultryGradingInspectionRecordTypes OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM AFS.dbo.GPSInspectionLocationRecords WHERE PoultryGradingClassInspectionRecordId = [AFS].[dbo].[PoultryGradingInspectionRecordTypes].Id ORDER BY Id) gps join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].[PoultryGradingInspectionRecordTypes].ClientId where AFS.dbo.[PoultryGradingInspectionRecordTypes].IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01' AND [AFS].[dbo].[PoultryGradingInspectionRecordTypes].ProductName IS NOT NULL AND [AFS].[dbo].[PoultryGradingInspectionRecordTypes].ProductName != ''
    UNION ALL
    SELECT 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber, [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ProductName as ProductName FROM AFS.dbo.PoultryLabelInspectionChecklistRecords OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM AFS.dbo.GPSInspectionLocationRecords WHERE PoultryLabelChecklistInspectionRecordId = [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].Id ORDER BY Id) gps join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ClientId where AFS.dbo.[PoultryLabelInspectionChecklistRecords].IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01' AND [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ProductName IS NOT NULL AND [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ProductName != ''
    UNION ALL
    SELECT 'EGGS' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForInspection as IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PoultryEggInspectionRecords].Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber, [AFS].[dbo].[PoultryEggInspectionRecords].EggProducer as ProductName FROM [AFS].[dbo].[PoultryEggInspectionRecords] OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM AFS.dbo.GPSInspectionLocationRecords WHERE PoultryEggInspectionRecordId = [AFS].[dbo].[PoultryEggInspectionRecords].Id ORDER BY Id) gps join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].[PoultryEggInspectionRecords].ClientId where AFS.dbo.[PoultryEggInspectionRecords].IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01'
    UNION ALL
    SELECT 'RAW' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, IsSampleTaken, InspectionTravelDistanceKm, [AFS].[dbo].[RawRMPInspectionRecordTypes].Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber, prod.NewProductItemDetails as ProductName FROM [AFS].[dbo].[RawRMPInspectionRecordTypes] OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM AFS.dbo.GPSInspectionLocationRecords WHERE RawRMPInspectionRecordId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id ORDER BY Id) gps JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod on prod.InspectionId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id join AFS.dbo.Clients clt on clt.Id = prod.ClientId where AFS.dbo.[RawRMPInspectionRecordTypes].IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01' AND prod.NewProductItemDetails IS NOT NULL AND prod.NewProductItemDetails != ''
    UNION ALL
    SELECT 'PMP' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PMPInspectionRecordTypes].Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber, prod.PMPItemDetails as ProductName FROM [AFS].[dbo].[PMPInspectionRecordTypes] OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM AFS.dbo.GPSInspectionLocationRecords WHERE PMPInspectionRecordId = [AFS].[dbo].[PMPInspectionRecordTypes].Id ORDER BY Id) gps JOIN AFS.dbo.PMPInspectedProductRecordTypes prod on prod.InspectionId = [AFS].[dbo].[PMPInspectionRecordTypes].Id join AFS.dbo.Clients clt on clt.Id = prod.ClientId where AFS.dbo.[PMPInspectionRecordTypes].IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01' AND prod.PMPItemDetails IS NOT NULL AND prod.PMPItemDetails != ''
'''

def test_poultry_commodity():
    """Test that the query works and POULTRY commodity is returned correctly"""

    print("=" * 80)
    print("TESTING POULTRY COMMODITY NAME CHANGE")
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

        # Execute query
        print("Executing FSA Inspection Query...")
        cursor = connection.cursor()
        cursor.execute(FSA_INSPECTION_QUERY)

        # Fetch results
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        print(f"[OK] Query executed successfully")
        print(f"[OK] Total records returned: {len(rows)}")
        print()

        # Count commodities
        commodity_counts = {}
        poultry_records = []

        for row in rows:
            row_dict = dict(zip(columns, row))
            commodity = row_dict.get('Commodity')

            # Count by commodity
            if commodity in commodity_counts:
                commodity_counts[commodity] += 1
            else:
                commodity_counts[commodity] = 1

            # Collect POULTRY records for verification
            if commodity == 'POULTRY':
                poultry_records.append(row_dict)

        # Display results
        print("COMMODITY BREAKDOWN:")
        print("-" * 80)
        for commodity, count in sorted(commodity_counts.items()):
            print(f"  {commodity}: {count} records")
        print()

        # Check for POULTRY (should exist)
        if 'POULTRY' in commodity_counts:
            print(f"[SUCCESS] Found {commodity_counts['POULTRY']} POULTRY records")
            print()

            # Show sample POULTRY records
            print("SAMPLE POULTRY RECORDS:")
            print("-" * 80)
            for i, record in enumerate(poultry_records[:5], 1):
                print(f"\n  Record #{i}:")
                print(f"    Inspection ID: {record.get('Id')}")
                print(f"    Client: {record.get('Client')}")
                print(f"    Commodity: {record.get('Commodity')}")
                print(f"    Product Name: {record.get('ProductName')}")
                print(f"    Date: {record.get('DateOfInspection')}")

            if len(poultry_records) > 5:
                print(f"\n  ... and {len(poultry_records) - 5} more POULTRY records")
        else:
            print("[WARNING] No POULTRY records found")

        print()

        # Check for POULTRY_LABEL (should NOT exist)
        if 'POULTRY_LABEL' in commodity_counts:
            print(f"[ERROR] Found {commodity_counts['POULTRY_LABEL']} POULTRY_LABEL records")
            print("  The old commodity name still exists in the results!")
        else:
            print("[SUCCESS] No POULTRY_LABEL records found (correctly changed to POULTRY)")

        print()
        print("=" * 80)
        print("TEST COMPLETED")
        print("=" * 80)

        # Close connection
        cursor.close()
        connection.close()

    except pymssql.Error as e:
        print(f"[ERROR] SQL Server Error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    test_poultry_commodity()
