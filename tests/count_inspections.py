import pymssql
from datetime import datetime

try:
    # Connect to SQL Server
    connection = pymssql.connect(
        server='102.67.140.12',
        port=1053,
        user='FSAUser2',
        password='password',
        database='AFS',
        timeout=30
    )
    cursor = connection.cursor()

    print("=" * 80)
    print("COUNTING INSPECTIONS FROM OCTOBER 1, 2025 ONWARDS")
    print("=" * 80)

    # Count POULTRY inspections
    cursor.execute("""
        SELECT COUNT(*)
        FROM AFS.dbo.PoultryLabelInspectionChecklistRecords
        WHERE IsActive = 1
        AND DateOfInspection >= '2025-10-01'
        AND ProductName IS NOT NULL
        AND ProductName != ''
    """)
    poultry_count = cursor.fetchone()[0]
    print(f"\n[POULTRY] Inspections: {poultry_count:,}")

    # Count EGGS inspections
    cursor.execute("""
        SELECT COUNT(*)
        FROM AFS.dbo.PoultryEggInspectionRecords
        WHERE IsActive = 1
        AND DateOfInspection >= '2025-10-01'
    """)
    eggs_count = cursor.fetchone()[0]
    print(f"[EGGS] Inspections: {eggs_count:,}")

    # Count RAW inspections
    cursor.execute("""
        SELECT COUNT(*)
        FROM AFS.dbo.RawRMPInspectionRecordTypes r
        JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod ON prod.InspectionId = r.Id
        WHERE r.IsActive = 1
        AND r.DateOfInspection >= '2025-10-01'
        AND prod.NewProductItemDetails IS NOT NULL
        AND prod.NewProductItemDetails != ''
    """)
    raw_count = cursor.fetchone()[0]
    print(f"[RAW] Inspections: {raw_count:,}")

    # Count PMP inspections
    cursor.execute("""
        SELECT COUNT(*)
        FROM AFS.dbo.PMPInspectionRecordTypes p
        JOIN AFS.dbo.PMPInspectedProductRecordTypes prod ON prod.InspectionId = p.Id
        WHERE p.IsActive = 1
        AND p.DateOfInspection >= '2025-10-01'
        AND prod.PMPItemDetails IS NOT NULL
        AND prod.PMPItemDetails != ''
    """)
    pmp_count = cursor.fetchone()[0]
    print(f"[PMP] Inspections: {pmp_count:,}")

    total_count = poultry_count + eggs_count + raw_count + pmp_count
    print(f"\n{'=' * 80}")
    print(f"[TOTAL] INSPECTIONS: {total_count:,}")
    print(f"{'=' * 80}")

    # Get date range
    cursor.execute("""
        SELECT MIN(DateOfInspection) as earliest, MAX(DateOfInspection) as latest
        FROM (
            SELECT DateOfInspection FROM AFS.dbo.PoultryLabelInspectionChecklistRecords
            WHERE IsActive = 1 AND DateOfInspection >= '2025-10-01'
            UNION ALL
            SELECT DateOfInspection FROM AFS.dbo.PoultryEggInspectionRecords
            WHERE IsActive = 1 AND DateOfInspection >= '2025-10-01'
            UNION ALL
            SELECT DateOfInspection FROM AFS.dbo.RawRMPInspectionRecordTypes
            WHERE IsActive = 1 AND DateOfInspection >= '2025-10-01'
            UNION ALL
            SELECT DateOfInspection FROM AFS.dbo.PMPInspectionRecordTypes
            WHERE IsActive = 1 AND DateOfInspection >= '2025-10-01'
        ) as all_dates
    """)
    date_range = cursor.fetchone()
    if date_range[0]:
        print(f"\n[DATE RANGE]:")
        print(f"   Earliest: {date_range[0]}")
        print(f"   Latest: {date_range[1]}")
        print(f"   Today: {datetime.now().date()}")

    cursor.close()
    connection.close()

except Exception as e:
    print(f"\n[ERROR]: {e}")
    import traceback
    traceback.print_exc()
