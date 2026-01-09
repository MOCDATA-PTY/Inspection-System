"""
Check SQL Server directly to see if inspection IDs exist in multiple commodity tables
"""
import pymssql
from datetime import datetime, timedelta

SQL_SERVER_CONFIG = {
    'server': '102.67.140.12',
    'port': 1053,
    'user': 'FSAUser2',
    'password': 'password',
    'database': 'AFS',
    'timeout': 60
}

print("=" * 80)
print("SQL SERVER DUPLICATE INSPECTION ID ANALYSIS")
print("=" * 80)

try:
    conn = pymssql.connect(**SQL_SERVER_CONFIG)
    cursor = conn.cursor(as_dict=True)
    print("\n[OK] Connected to SQL Server successfully")

    # Date range - last 90 days
    ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    print(f"[OK] Checking inspections from: {ninety_days_ago}")

    # Check a sample of inspection IDs we found duplicated (from earlier analysis)
    sample_ids = [8487, 8488, 8489, 8490, 8491, 8492, 6342]

    print("\n" + "=" * 80)
    print("CHECKING SAMPLE INSPECTION IDs IN ALL TABLES")
    print("=" * 80)

    for insp_id in sample_ids:
        print(f"\n--- Inspection ID: {insp_id} ---")

        # Check PoultryQuidInspectionRecordTypes
        cursor.execute(f"""
            SELECT Id, ProductName, DateOfInspection, 'POULTRY_QUID' as TableName
            FROM PoultryQuidInspectionRecordTypes
            WHERE Id = {insp_id} AND IsActive = 1
        """)
        poultry_quid = cursor.fetchall()

        # Check PoultryGradingInspectionRecordTypes
        cursor.execute(f"""
            SELECT Id, ProductName, DateOfInspection, 'POULTRY_GRADING' as TableName
            FROM PoultryGradingInspectionRecordTypes
            WHERE Id = {insp_id} AND IsActive = 1
        """)
        poultry_grading = cursor.fetchall()

        # Check PoultryLabelInspectionChecklistRecords
        cursor.execute(f"""
            SELECT Id, ProductName, DateOfInspection, 'POULTRY_LABEL' as TableName
            FROM PoultryLabelInspectionChecklistRecords
            WHERE Id = {insp_id} AND IsActive = 1
        """)
        poultry_label = cursor.fetchall()

        # Check PoultryEggInspectionRecords
        cursor.execute(f"""
            SELECT Id, EggProducer as ProductName, DateOfInspection, 'EGGS' as TableName
            FROM PoultryEggInspectionRecords
            WHERE Id = {insp_id} AND IsActive = 1
        """)
        eggs = cursor.fetchall()

        # Check RawRMPInspectionRecordTypes (with products)
        cursor.execute(f"""
            SELECT i.Id, p.NewProductItemDetails as ProductName, i.DateOfInspection, 'RAW_RMP' as TableName
            FROM RawRMPInspectionRecordTypes i
            LEFT JOIN RawRMPInspectedProductRecordTypes p ON p.InspectionId = i.Id
            WHERE i.Id = {insp_id} AND i.IsActive = 1
        """)
        raw = cursor.fetchall()

        # Check PMPInspectionRecordTypes (with products)
        cursor.execute(f"""
            SELECT i.Id, p.PMPItemDetails as ProductName, i.DateOfInspection, 'PMP' as TableName
            FROM PMPInspectionRecordTypes i
            LEFT JOIN PMPInspectedProductRecordTypes p ON p.InspectionId = i.Id
            WHERE i.Id = {insp_id} AND i.IsActive = 1
        """)
        pmp = cursor.fetchall()

        # Combine all results
        all_results = poultry_quid + poultry_grading + poultry_label + eggs + raw + pmp

        if len(all_results) > 0:
            print(f"  Found in {len(all_results)} table(s):")
            for result in all_results:
                print(f"    - {result['TableName']}: Product='{result['ProductName']}', Date={result['DateOfInspection']}")

            if len(all_results) > 1:
                print(f"  [ERROR] DUPLICATE! Same inspection ID in {len(all_results)} different tables!")
        else:
            print(f"  Not found in any table (might be older than 90 days)")

    # Now do a comprehensive check for ALL duplicates
    print("\n" + "=" * 80)
    print("COMPREHENSIVE DUPLICATE CHECK - ALL INSPECTION IDs")
    print("=" * 80)

    # Get all inspection IDs from each table
    tables_to_check = [
        ('PoultryQuidInspectionRecordTypes', 'POULTRY'),
        ('PoultryGradingInspectionRecordTypes', 'POULTRY'),
        ('PoultryLabelInspectionChecklistRecords', 'POULTRY'),
        ('PoultryEggInspectionRecords', 'EGGS'),
        ('RawRMPInspectionRecordTypes', 'RAW'),
        ('PMPInspectionRecordTypes', 'PMP'),
    ]

    # Collect all IDs from each table
    all_ids = {}
    for table_name, commodity in tables_to_check:
        cursor.execute(f"""
            SELECT Id
            FROM {table_name}
            WHERE DateOfInspection >= '{ninety_days_ago}' AND IsActive = 1
        """)
        ids = [row['Id'] for row in cursor.fetchall()]
        print(f"\n{table_name} ({commodity}): {len(ids)} inspections")

        for insp_id in ids:
            if insp_id not in all_ids:
                all_ids[insp_id] = []
            all_ids[insp_id].append((table_name, commodity))

    # Find duplicates
    duplicates = {id: tables for id, tables in all_ids.items() if len(tables) > 1}

    print(f"\n{'=' * 80}")
    print(f"RESULTS: Found {len(duplicates)} inspection IDs in multiple tables")
    print(f"{'=' * 80}")

    if duplicates:
        print(f"\nShowing first 30 duplicates:")
        print(f"{'Inspection ID':<15} {'Count':<10} {'Tables':<50}")
        print("-" * 75)

        for insp_id, tables in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:30]:
            table_names = ', '.join([f"{t[0].split('Inspection')[0]}({t[1]})" for t in tables])
            print(f"{insp_id:<15} {len(tables):<10} {table_names:<50}")

        # Analyze patterns
        print("\n" + "=" * 80)
        print("DUPLICATE PATTERNS")
        print("=" * 80)

        patterns = {}
        for insp_id, tables in duplicates.items():
            commodities = tuple(sorted(set([t[1] for t in tables])))
            if commodities not in patterns:
                patterns[commodities] = 0
            patterns[commodities] += 1

        print(f"\n{'Commodity Combination':<40} {'Count':<10}")
        print("-" * 50)
        for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
            pattern_str = ' + '.join(pattern)
            print(f"{pattern_str:<40} {count:<10}")

    # Check specific case: Are RAW and PMP inspections actually different products?
    print("\n" + "=" * 80)
    print("DETAILED CHECK: RAW + PMP DUPLICATES")
    print("=" * 80)
    print("\nAre these ACTUALLY duplicates or different products from same inspection?")

    # Get a sample RAW+PMP duplicate
    raw_pmp_dupes = [id for id, tables in duplicates.items()
                     if any(t[1] == 'RAW' for t in tables) and any(t[1] == 'PMP' for t in tables)]

    if raw_pmp_dupes:
        sample_id = raw_pmp_dupes[0]
        print(f"\nExamining Inspection ID {sample_id}:")

        # Get RAW products
        cursor.execute(f"""
            SELECT p.NewProductItemDetails as ProductName, c.Name as ClientName
            FROM RawRMPInspectionRecordTypes i
            JOIN RawRMPInspectedProductRecordTypes p ON p.InspectionId = i.Id
            LEFT JOIN Clients c ON c.Id = p.ClientId
            WHERE i.Id = {sample_id}
        """)
        raw_products = cursor.fetchall()

        print(f"\n  RAW products ({len(raw_products)}):")
        for p in raw_products:
            print(f"    - {p['ProductName']} ({p['ClientName']})")

        # Get PMP products
        cursor.execute(f"""
            SELECT p.PMPItemDetails as ProductName, c.Name as ClientName
            FROM PMPInspectionRecordTypes i
            JOIN PMPInspectedProductRecordTypes p ON p.InspectionId = i.Id
            LEFT JOIN Clients c ON c.Id = p.ClientId
            WHERE i.Id = {sample_id}
        """)
        pmp_products = cursor.fetchall()

        print(f"\n  PMP products ({len(pmp_products)}):")
        for p in pmp_products:
            print(f"    - {p['ProductName']} ({p['ClientName']})")

        print("\n  ANALYSIS:")
        if len(raw_products) > 0 and len(pmp_products) > 0:
            print("    This inspection has BOTH RAW and PMP products")
            print("    This is LEGITIMATE if inspector checked multiple product types")
            print("    BUT the system should display them as ONE inspection with multiple products")
        else:
            print("    Only one product type found - this is a TRUE duplicate!")

    conn.close()

except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
Based on this analysis:

1. If inspection IDs appear in multiple tables WITH DIFFERENT PRODUCTS:
   -> This is CORRECT - one inspection can have multiple product types
   -> System should GROUP them as ONE inspection with multiple products

2. If inspection IDs appear in multiple tables WITH SAME/SIMILAR PRODUCTS:
   -> This is INCORRECT - true duplicate entry
   -> Data entry error in SQL Server

3. If wors products appear in BOTH RAW and PMP tables:
   -> Check if they're different products or true duplicates
   -> Wors should ONLY be in PMP, never in RAW
""")
