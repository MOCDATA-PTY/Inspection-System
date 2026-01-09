"""Check Amans meat & deli data from SQL Server (source of truth)"""
import pyodbc
from collections import defaultdict

# SQL Server connection (AFS production database)
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=102.67.140.12,1053;'
    'DATABASE=AFS;'
    'UID=FSAUser2;'
    'PWD=password;'
    'TrustServerCertificate=yes;'
    'Encrypt=yes;'
)

print("=" * 100)
print("CHECKING AMANS MEAT & DELI IN SQL SERVER (SOURCE)")
print("=" * 100)

try:
    conn = pyodbc.connect(conn_str, timeout=10)
    cursor = conn.cursor()

    # Search for any Amans RAW and PMP inspections in December 2025
    query = """
    SELECT
        'RAW' as Commodity,
        raw_insp.Id as InspectionID,
        raw_insp.DateOfInspection,
        raw_insp.InspectorId as InspectorName,
        clt.Name as ClientName,
        prod.ProductName,
        prod.IsSampleTaken,
        prod.Fat,
        prod.Protein,
        NULL as Calcium,
        prod.DNA,
        raw_insp.InspectionHours as Hours,
        raw_insp.KMsTravelled as KMTraveled
    FROM AFS.dbo.RawRMPInspectionRecordTypes raw_insp
    JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod ON prod.InspectionId = raw_insp.Id
    JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
    WHERE raw_insp.IsActive = 1
        AND LOWER(clt.Name) LIKE '%amans%'
        AND raw_insp.DateOfInspection >= '2025-12-01'
        AND raw_insp.DateOfInspection <= '2025-12-31'

    UNION ALL

    SELECT
        'PMP' as Commodity,
        pmp_insp.Id as InspectionID,
        pmp_insp.DateOfInspection,
        pmp_insp.InspectorId as InspectorName,
        clt.Name as ClientName,
        prod.ProductName,
        prod.IsSampleTaken,
        prod.Fat,
        prod.Protein,
        prod.Calcium,
        NULL as DNA,
        pmp_insp.InspectionHours as Hours,
        pmp_insp.KMsTravelled as KMTraveled
    FROM AFS.dbo.PMPInspectionRecordTypes pmp_insp
    JOIN AFS.dbo.PMPInspectedProductRecordTypes prod ON prod.InspectionId = pmp_insp.Id
    JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
    WHERE pmp_insp.IsActive = 1
        AND LOWER(clt.Name) LIKE '%amans%'
        AND pmp_insp.DateOfInspection >= '2025-12-01'
        AND pmp_insp.DateOfInspection <= '2025-12-31'

    ORDER BY DateOfInspection, ClientName, Commodity, ProductName
    """

    print(f"\nQuerying SQL Server for Amans inspections in December 2025...\n")
    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        print("No Amans inspections found in December 2025")

        # Try to find any Amans inspections (recent 20)
        query2 = """
        SELECT TOP 20
            'RAW' as Commodity,
            raw_insp.DateOfInspection,
            clt.Name as ClientName,
            prod.ProductName,
            raw_insp.InspectionHours as Hours,
            raw_insp.KMsTravelled as KMTraveled
        FROM AFS.dbo.RawRMPInspectionRecordTypes raw_insp
        JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod ON prod.InspectionId = raw_insp.Id
        JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
        WHERE raw_insp.IsActive = 1
            AND LOWER(clt.Name) LIKE '%amans%'

        UNION ALL

        SELECT TOP 20
            'PMP' as Commodity,
            pmp_insp.DateOfInspection,
            clt.Name as ClientName,
            prod.ProductName,
            pmp_insp.InspectionHours as Hours,
            pmp_insp.KMsTravelled as KMTraveled
        FROM AFS.dbo.PMPInspectionRecordTypes pmp_insp
        JOIN AFS.dbo.PMPInspectedProductRecordTypes prod ON prod.InspectionId = pmp_insp.Id
        JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
        WHERE pmp_insp.IsActive = 1
            AND LOWER(clt.Name) LIKE '%amans%'

        ORDER BY DateOfInspection DESC
        """
        cursor.execute(query2)
        rows2 = cursor.fetchall()
        print(f"\nFound {len(rows2)} Amans inspections (recent 20):")
        for row in rows2:
            print(f"  {row.DateOfInspection}: {row.Commodity} - {row.ProductName} (Hours: {row.Hours}, KM: {row.KMTraveled})")
    else:
        print(f"Found {len(rows)} inspections\n")
        print("=" * 100)

        # Group by visit
        visits = defaultdict(list)
        for row in rows:
            visit_key = (
                str(row.DateOfInspection) if row.DateOfInspection else '',
                row.InspectorName or '',
                row.ClientName or ''
            )
            visits[visit_key].append(row)

        print(f"Grouped into {len(visits)} visit(s)\n")

        # Process each visit
        for visit_key, visit_rows in visits.items():
            date_str, inspector_name, client_name = visit_key

            print("=" * 100)
            print(f"VISIT: {client_name}")
            print(f"Date: {date_str}")
            print(f"Inspector: {inspector_name}")
            print("=" * 100)

            # Get hours/km from first inspection
            first = visit_rows[0]
            original_hours = float(first.Hours) if first.Hours else 0
            original_km = float(first.KMTraveled) if first.KMTraveled else 0

            print(f"\n[SQL SERVER DATABASE VALUES]")
            print(f"  First Product Hours: {original_hours}")
            print(f"  First Product KM: {original_km}")

            # Show all products
            print(f"\n[ALL PRODUCTS IN THIS VISIT]")
            pmp_count = 0
            raw_count = 0

            for i, row in enumerate(visit_rows, 1):
                commodity = row.Commodity or ''
                is_pmp = 'PMP' in commodity.upper()
                is_raw = 'RAW' in commodity.upper()

                if is_pmp:
                    pmp_count += 1
                if is_raw:
                    raw_count += 1

                print(f"\n  {i}. {commodity} - {row.ProductName}")
                print(f"     InspectionID: {row.InspectionID}")
                print(f"     Hours: {row.Hours}, KM: {row.KMTraveled}")
                print(f"     Sample Taken: {row.IsSampleTaken}")
                print(f"     Tests: Fat={row.Fat}, Protein={row.Protein}, Calcium={row.Calcium}, DNA={row.DNA}")

            # Check commodity breakdown
            has_both = pmp_count > 0 and raw_count > 0

            print(f"\n[COMMODITY BREAKDOWN]")
            print(f"  PMP Products: {pmp_count}")
            print(f"  RAW Products: {raw_count}")
            print(f"  Has Both Types: {has_both}")

            # Show what SHOULD be generated
            print(f"\n[EXPECTED LINE ITEMS FOR EXPORT]")
            print(f"\n--- HOURS/KM Line Items ---")

            if has_both:
                split_hours = original_hours / 2
                split_km = original_km / 2

                print(f"  PMP 060: Inspection Hours = {split_hours}")
                print(f"  PMP 061: Travel KM = {split_km}")
                print(f"  RAW 050: Inspection Hours = {split_hours}")
                print(f"  RAW 051: Travel KM = {split_km}")
            else:
                commodity_type = 'RAW' if raw_count > 0 else 'PMP'
                print(f"  {commodity_type} 050/060: Inspection Hours = {original_hours}")
                print(f"  {commodity_type} 051/061: Travel KM = {original_km}")

            # Check for test line items
            print(f"\n--- TEST Line Items ---")

            pmp_needs_fat = any(row.Fat and row.IsSampleTaken and 'PMP' in (row.Commodity or '').upper() for row in visit_rows)
            pmp_needs_protein = any(row.Protein and row.IsSampleTaken and 'PMP' in (row.Commodity or '').upper() for row in visit_rows)
            pmp_needs_calcium = any(row.Calcium and row.IsSampleTaken and 'PMP' in (row.Commodity or '').upper() for row in visit_rows)

            raw_needs_fat = any(row.Fat and row.IsSampleTaken and 'RAW' in (row.Commodity or '').upper() for row in visit_rows)
            raw_needs_protein = any(row.Protein and row.IsSampleTaken and 'RAW' in (row.Commodity or '').upper() for row in visit_rows)
            raw_needs_dna = any(row.DNA and row.IsSampleTaken and 'RAW' in (row.Commodity or '').upper() for row in visit_rows)

            if pmp_count > 0:
                print(f"  PMP Tests:")
                if pmp_needs_fat:
                    print(f"    PMP 062: Fat Content test")
                if pmp_needs_protein:
                    print(f"    PMP 064: Protein Content test")
                if pmp_needs_calcium:
                    print(f"    PMP 065: Calcium Content test")
                if not (pmp_needs_fat or pmp_needs_protein or pmp_needs_calcium):
                    print(f"    (No PMP tests needed)")

            if raw_count > 0:
                print(f"  RAW Tests:")
                if raw_needs_fat:
                    print(f"    RAW 052: Fat Content test")
                if raw_needs_protein:
                    print(f"    RAW 054: Protein Content test")
                if raw_needs_dna:
                    print(f"    RAW 053: DNA test")
                if not (raw_needs_fat or raw_needs_protein or raw_needs_dna):
                    print(f"    (No RAW tests needed)")

            # Count total line items
            count = 4 if has_both else 2  # hours/km
            count += sum([pmp_needs_fat, pmp_needs_protein, pmp_needs_calcium])
            count += sum([raw_needs_fat, raw_needs_protein, raw_needs_dna])

            print(f"\n[TOTAL EXPECTED LINE ITEMS]: {count} line items")
            print()

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error connecting to SQL Server: {e}")
    import traceback
    traceback.print_exc()

print("=" * 100)
