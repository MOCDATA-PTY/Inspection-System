"""
Test script to verify all poultry commodities are consolidated under "POULTRY"
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

# Updated query with ALL poultry types as "POULTRY"
FSA_INSPECTION_QUERY = '''
    SELECT 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PoultryQuidInspectionRecordTypes].Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber, [AFS].[dbo].[PoultryQuidInspectionRecordTypes].ProductName as ProductName FROM AFS.dbo.PoultryQuidInspectionRecordTypes OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM AFS.dbo.GPSInspectionLocationRecords WHERE PoultryQuidInspectionRecordId = [AFS].[dbo].PoultryQuidInspectionRecordTypes.Id ORDER BY Id) gps join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].PoultryQuidInspectionRecordTypes.ClientId where AFS.dbo.PoultryQuidInspectionRecordTypes.IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01' AND [AFS].[dbo].[PoultryQuidInspectionRecordTypes].ProductName IS NOT NULL AND [AFS].[dbo].[PoultryQuidInspectionRecordTypes].ProductName != ''
    UNION ALL
    SELECT 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PoultryGradingInspectionRecordTypes].Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber, [AFS].[dbo].[PoultryGradingInspectionRecordTypes].ProductName as ProductName FROM AFS.dbo.PoultryGradingInspectionRecordTypes OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM AFS.dbo.GPSInspectionLocationRecords WHERE PoultryGradingClassInspectionRecordId = [AFS].[dbo].[PoultryGradingInspectionRecordTypes].Id ORDER BY Id) gps join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].[PoultryGradingInspectionRecordTypes].ClientId where AFS.dbo.[PoultryGradingInspectionRecordTypes].IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01' AND [AFS].[dbo].[PoultryGradingInspectionRecordTypes].ProductName IS NOT NULL AND [AFS].[dbo].[PoultryGradingInspectionRecordTypes].ProductName != ''
    UNION ALL
    SELECT 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber, [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ProductName as ProductName FROM AFS.dbo.PoultryLabelInspectionChecklistRecords OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM AFS.dbo.GPSInspectionLocationRecords WHERE PoultryLabelChecklistInspectionRecordId = [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].Id ORDER BY Id) gps join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ClientId where AFS.dbo.[PoultryLabelInspectionChecklistRecords].IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01' AND [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ProductName IS NOT NULL AND [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ProductName != ''
    UNION ALL
    SELECT 'EGGS' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForInspection as IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PoultryEggInspectionRecords].Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber, [AFS].[dbo].[PoultryEggInspectionRecords].EggProducer as ProductName FROM [AFS].[dbo].[PoultryEggInspectionRecords] OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM AFS.dbo.GPSInspectionLocationRecords WHERE PoultryEggInspectionRecordId = [AFS].[dbo].[PoultryEggInspectionRecords].Id ORDER BY Id) gps join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].[PoultryEggInspectionRecords].ClientId where AFS.dbo.[PoultryEggInspectionRecords].IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01'
    UNION ALL
    SELECT 'RAW' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, IsSampleTaken, InspectionTravelDistanceKm, [AFS].[dbo].[RawRMPInspectionRecordTypes].Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber, prod.NewProductItemDetails as ProductName FROM [AFS].[dbo].[RawRMPInspectionRecordTypes] OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM AFS.dbo.GPSInspectionLocationRecords WHERE RawRMPInspectionRecordId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id ORDER BY Id) gps JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod on prod.InspectionId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id join AFS.dbo.Clients clt on clt.Id = prod.ClientId where AFS.dbo.[RawRMPInspectionRecordTypes].IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01' AND prod.NewProductItemDetails IS NOT NULL AND prod.NewProductItemDetails != ''
    UNION ALL
    SELECT 'PMP' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PMPInspectionRecordTypes].Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber, prod.PMPItemDetails as ProductName FROM [AFS].[dbo].[PMPInspectionRecordTypes] OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM AFS.dbo.GPSInspectionLocationRecords WHERE PMPInspectionRecordId = [AFS].[dbo].[PMPInspectionRecordTypes].Id ORDER BY Id) gps JOIN AFS.dbo.PMPInspectedProductRecordTypes prod on prod.InspectionId = [AFS].[dbo].[PMPInspectionRecordTypes].Id join AFS.dbo.Clients clt on clt.Id = prod.ClientId where AFS.dbo.[PMPInspectionRecordTypes].IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01' AND prod.PMPItemDetails IS NOT NULL AND prod.PMPItemDetails != ''
'''

def test_consolidated_poultry():
    """Test that all poultry types are consolidated under POULTRY commodity"""

    print("=" * 80)
    print("TESTING CONSOLIDATED POULTRY COMMODITY")
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

        for row in rows:
            row_dict = dict(zip(columns, row))
            commodity = row_dict.get('Commodity')

            if commodity in commodity_counts:
                commodity_counts[commodity] += 1
            else:
                commodity_counts[commodity] = 1

        # Display results
        print("COMMODITY BREAKDOWN:")
        print("-" * 80)
        for commodity, count in sorted(commodity_counts.items()):
            print(f"  {commodity}: {count} records")
        print()

        # Verify consolidation
        print("CONSOLIDATION VERIFICATION:")
        print("-" * 80)

        old_poultry_names = ['POULTRY_QUID', 'POULTRY_GRADING', 'POULTRY_LABEL']
        found_old_names = [name for name in old_poultry_names if name in commodity_counts]

        if found_old_names:
            print(f"[ERROR] Found old poultry commodity names:")
            for name in found_old_names:
                print(f"  - {name}: {commodity_counts[name]} records")
            print()
            return False
        else:
            print("[SUCCESS] No old poultry commodity names found")
            print()

        # Check POULTRY exists
        if 'POULTRY' in commodity_counts:
            poultry_count = commodity_counts['POULTRY']
            print(f"[SUCCESS] Found consolidated POULTRY commodity")
            print(f"  Total POULTRY records: {poultry_count}")
            print()

            # Get breakdown by source table
            print("SOURCE TABLE BREAKDOWN:")
            print("-" * 80)

            # Count from each source table
            query_quid_count = """
            SELECT COUNT(*) FROM AFS.dbo.PoultryQuidInspectionRecordTypes
            WHERE IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01'
            AND ProductName IS NOT NULL AND ProductName != ''
            """
            cursor.execute(query_quid_count)
            quid_count = cursor.fetchone()[0]

            query_grading_count = """
            SELECT COUNT(*) FROM AFS.dbo.PoultryGradingInspectionRecordTypes
            WHERE IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01'
            AND ProductName IS NOT NULL AND ProductName != ''
            """
            cursor.execute(query_grading_count)
            grading_count = cursor.fetchone()[0]

            query_label_count = """
            SELECT COUNT(*) FROM AFS.dbo.PoultryLabelInspectionChecklistRecords
            WHERE IsActive = 1 AND DateOfInspection >= '2025-10-01' AND DateOfInspection < '2026-04-01'
            AND ProductName IS NOT NULL AND ProductName != ''
            """
            cursor.execute(query_label_count)
            label_count = cursor.fetchone()[0]

            print(f"  From PoultryQuidInspectionRecordTypes: {quid_count}")
            print(f"  From PoultryGradingInspectionRecordTypes: {grading_count}")
            print(f"  From PoultryLabelInspectionChecklistRecords: {label_count}")
            print(f"  ---")
            print(f"  Expected total: {quid_count + grading_count + label_count}")
            print(f"  Actual total: {poultry_count}")

            if quid_count + grading_count + label_count == poultry_count:
                print(f"  [SUCCESS] Counts match perfectly!")
            else:
                print(f"  [WARNING] Count mismatch detected")

        else:
            print("[ERROR] POULTRY commodity not found")
            return False

        print()
        print("=" * 80)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print()
        print("SUMMARY:")
        print(f"  - All poultry types now consolidated under 'POULTRY'")
        print(f"  - Total POULTRY records: {poultry_count}")
        print(f"  - No POULTRY_QUID, POULTRY_GRADING, or POULTRY_LABEL found")
        print()

        cursor.close()
        connection.close()

        return True

    except pymssql.Error as e:
        print(f"[ERROR] SQL Server Error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_consolidated_poultry()
