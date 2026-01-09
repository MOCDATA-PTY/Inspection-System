"""
Generate a detailed report of database issues to send to the database team
"""
import pymssql
from datetime import datetime

SQL_SERVER_CONFIG = {
    'server': '102.67.140.12',
    'port': 1053,
    'user': 'FSAUser2',
    'password': 'password',
    'database': 'AFS',
    'timeout': 60
}

print("=" * 80)
print("DATABASE ISSUE REPORT FOR SQL SERVER TEAM")
print("Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80)

try:
    conn = pymssql.connect(**SQL_SERVER_CONFIG)
    cursor = conn.cursor(as_dict=True)
    print("\n[Connected to SQL Server: 102.67.140.12:1053/AFS]")

    # Problem inspection IDs
    problem_ids = [8487, 8488, 6342]

    print("\n" + "=" * 80)
    print("ISSUE: INSPECTION IDs ARE REUSED ACROSS DIFFERENT COMMODITY TABLES")
    print("=" * 80)
    print("\nThe same Inspection ID exists in multiple tables with DIFFERENT data:")
    print("- Different inspection dates")
    print("- Different clients")
    print("- Different products")
    print("\nThis causes data integrity issues when querying across tables.")

    for insp_id in problem_ids:
        print("\n" + "=" * 80)
        print(f"EXAMPLE: INSPECTION ID {insp_id}")
        print("=" * 80)

        # Check RawRMPInspectionRecordTypes
        print(f"\n--- TABLE: RawRMPInspectionRecordTypes ---")
        cursor.execute(f"""
            SELECT TOP 1
                i.Id,
                i.DateOfInspection,
                i.StartOfInspection,
                i.EndOfInspection,
                i.InspectorId,
                i.IsActive,
                p.NewProductItemDetails as ProductName,
                c.Name as ClientName,
                c.InternalAccountNumber
            FROM RawRMPInspectionRecordTypes i
            LEFT JOIN RawRMPInspectedProductRecordTypes p ON p.InspectionId = i.Id
            LEFT JOIN Clients c ON c.Id = p.ClientId
            WHERE i.Id = {insp_id}
        """)
        raw_result = cursor.fetchone()

        if raw_result:
            print(f"FOUND - Inspection exists in RAW table:")
            print(f"  Inspection ID:        {raw_result['Id']}")
            print(f"  Date:                 {raw_result['DateOfInspection']}")
            print(f"  Time:                 {raw_result['StartOfInspection']} - {raw_result['EndOfInspection']}")
            print(f"  Client:               {raw_result['ClientName']}")
            print(f"  Account Number:       {raw_result['InternalAccountNumber']}")
            print(f"  Product:              {raw_result['ProductName']}")
            print(f"  Inspector ID:         {raw_result['InspectorId']}")
            print(f"  Active:               {raw_result['IsActive']}")

        # Check PMPInspectionRecordTypes
        print(f"\n--- TABLE: PMPInspectionRecordTypes ---")
        cursor.execute(f"""
            SELECT TOP 1
                i.Id,
                i.DateOfInspection,
                i.StartOfInspection,
                i.EndOfInspection,
                i.InspectorId,
                i.IsActive,
                p.PMPItemDetails as ProductName,
                c.Name as ClientName,
                c.InternalAccountNumber
            FROM PMPInspectionRecordTypes i
            LEFT JOIN PMPInspectedProductRecordTypes p ON p.InspectionId = i.Id
            LEFT JOIN Clients c ON c.Id = p.ClientId
            WHERE i.Id = {insp_id}
        """)
        pmp_result = cursor.fetchone()

        if pmp_result:
            print(f"FOUND - Inspection exists in PMP table:")
            print(f"  Inspection ID:        {pmp_result['Id']}")
            print(f"  Date:                 {pmp_result['DateOfInspection']}")
            print(f"  Time:                 {pmp_result['StartOfInspection']} - {pmp_result['EndOfInspection']}")
            print(f"  Client:               {pmp_result['ClientName']}")
            print(f"  Account Number:       {pmp_result['InternalAccountNumber']}")
            print(f"  Product:              {pmp_result['ProductName']}")
            print(f"  Inspector ID:         {pmp_result['InspectorId']}")
            print(f"  Active:               {pmp_result['IsActive']}")

        # Check PoultryLabelInspectionChecklistRecords
        print(f"\n--- TABLE: PoultryLabelInspectionChecklistRecords ---")
        cursor.execute(f"""
            SELECT TOP 1
                i.Id,
                i.DateOfInspection,
                i.StartOfInspection,
                i.EndOfInspection,
                i.InspectorId,
                i.IsActive,
                i.ProductName,
                c.Name as ClientName,
                c.InternalAccountNumber
            FROM PoultryLabelInspectionChecklistRecords i
            LEFT JOIN Clients c ON c.Id = i.ClientId
            WHERE i.Id = {insp_id}
        """)
        poultry_result = cursor.fetchone()

        if poultry_result:
            print(f"FOUND - Inspection exists in POULTRY table:")
            print(f"  Inspection ID:        {poultry_result['Id']}")
            print(f"  Date:                 {poultry_result['DateOfInspection']}")
            print(f"  Time:                 {poultry_result['StartOfInspection']} - {poultry_result['EndOfInspection']}")
            print(f"  Client:               {poultry_result['ClientName']}")
            print(f"  Account Number:       {poultry_result['InternalAccountNumber']}")
            print(f"  Product:              {poultry_result['ProductName']}")
            print(f"  Inspector ID:         {poultry_result['InspectorId']}")
            print(f"  Active:               {poultry_result['IsActive']}")

        # Analysis
        print(f"\n--- ANALYSIS ---")
        tables_found = []
        if raw_result:
            tables_found.append('RAW')
        if pmp_result:
            tables_found.append('PMP')
        if poultry_result:
            tables_found.append('POULTRY')

        if len(tables_found) > 1:
            print(f"[ERROR] Inspection ID {insp_id} found in {len(tables_found)} tables: {', '.join(tables_found)}")

            # Compare dates
            dates = []
            if raw_result:
                dates.append(('RAW', raw_result['DateOfInspection']))
            if pmp_result:
                dates.append(('PMP', pmp_result['DateOfInspection']))
            if poultry_result:
                dates.append(('POULTRY', poultry_result['DateOfInspection']))

            unique_dates = set([d[1] for d in dates])
            if len(unique_dates) > 1:
                print(f"[ERROR] DIFFERENT DATES - This proves these are DIFFERENT inspections!")
                for table, date in dates:
                    print(f"        {table}: {date}")
            else:
                print(f"[WARNING] Same date across tables - might be one inspection with multiple products")

            # Compare clients
            clients = []
            if raw_result and raw_result['ClientName']:
                clients.append(('RAW', raw_result['ClientName']))
            if pmp_result and pmp_result['ClientName']:
                clients.append(('PMP', pmp_result['ClientName']))
            if poultry_result and poultry_result['ClientName']:
                clients.append(('POULTRY', poultry_result['ClientName']))

            unique_clients = set([c[1] for c in clients if c[1]])
            if len(unique_clients) > 1:
                print(f"[ERROR] DIFFERENT CLIENTS - This proves these are DIFFERENT inspections!")
                for table, client in clients:
                    print(f"        {table}: {client}")

    # Show table structures
    print("\n" + "=" * 80)
    print("TABLE STRUCTURES")
    print("=" * 80)

    tables = [
        'RawRMPInspectionRecordTypes',
        'PMPInspectionRecordTypes',
        'PoultryLabelInspectionChecklistRecords',
        'PoultryQuidInspectionRecordTypes',
        'PoultryGradingInspectionRecordTypes',
        'PoultryEggInspectionRecords'
    ]

    for table_name in tables:
        print(f"\n{table_name}:")
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name}'
            AND COLUMN_NAME IN ('Id', 'DateOfInspection', 'ClientId', 'InspectorId', 'IsActive')
            ORDER BY ORDINAL_POSITION
        """)
        columns = cursor.fetchall()
        for col in columns:
            nullable = 'NULL' if col['IS_NULLABLE'] == 'YES' else 'NOT NULL'
            max_len = f"({col['CHARACTER_MAXIMUM_LENGTH']})" if col['CHARACTER_MAXIMUM_LENGTH'] else ''
            print(f"  {col['COLUMN_NAME']:<30} {col['DATA_TYPE']}{max_len:<15} {nullable}")

    # Get ID ranges for each table
    print("\n" + "=" * 80)
    print("INSPECTION ID RANGES BY TABLE (Last 90 days)")
    print("=" * 80)

    from datetime import datetime, timedelta
    ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    for table_name in tables:
        try:
            cursor.execute(f"""
                SELECT
                    MIN(Id) as MinId,
                    MAX(Id) as MaxId,
                    COUNT(*) as TotalCount
                FROM {table_name}
                WHERE DateOfInspection >= '{ninety_days_ago}'
                AND IsActive = 1
            """)
            result = cursor.fetchone()
            if result and result['TotalCount'] > 0:
                print(f"{table_name}:")
                print(f"  ID Range: {result['MinId']} to {result['MaxId']}")
                print(f"  Total Active Inspections: {result['TotalCount']}")
                print(f"  Overlap Risk: HIGH (IDs {result['MinId']}-{result['MaxId']} may exist in other tables)")
        except Exception as e:
            print(f"{table_name}: Error - {e}")

    conn.close()

    # Summary for database team
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS FOR DATABASE TEAM")
    print("=" * 80)
    print("""
ISSUE SUMMARY:
- Inspection IDs are NOT globally unique across commodity tables
- Each table (RAW, PMP, POULTRY, EGGS) uses its own ID sequence
- This causes the SAME ID to represent DIFFERENT inspections in different tables

EVIDENCE:
- Inspection 8487 in RAW table: Sep 3, 2025, Pick n Pay, Braaiwors
- Inspection 8487 in PMP table: Nov 17, 2025, Feiners, Polony
- These are DIFFERENT inspections with DIFFERENT dates and clients!

IMPACT:
- Data integrity issues when querying across tables
- Cannot reliably join data using only Inspection ID
- Reporting systems get confused about which inspection is which

RECOMMENDED SOLUTIONS:

Option 1: Create Global Inspection ID Sequence
- Create a single sequence/identity that all tables share
- ALTER TABLE statements to use SEQUENCE object
- Ensures globally unique IDs

Option 2: Add Composite Primary Key
- Use (TableName + InspectionID) as unique identifier
- Add a "SourceTable" column to track which table the record came from
- Update all queries to use composite key

Option 3: Prefix IDs by Commodity
- RAW inspections: 1000000 - 1999999
- PMP inspections: 2000000 - 2999999
- POULTRY inspections: 3000000 - 3999999
- EGGS inspections: 4000000 - 4999999

URGENT ACTION NEEDED:
This is a fundamental database design issue that must be resolved at the
SQL Server level. Application-level workarounds are not sustainable.
""")

except Exception as e:
    print(f"\n[ERROR] Database connection failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("END OF REPORT")
print("=" * 80)
print("\nSave this report and send to the SQL Server database team.")
