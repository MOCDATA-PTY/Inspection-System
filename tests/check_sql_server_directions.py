"""
Check SQL Server source database for direction field values
"""
import pyodbc

print("=" * 100)
print("CHECKING SQL SERVER FOR DIRECTION DATA")
print("=" * 100)

# Connect to SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=102.67.140.12,1053;'
    'DATABASE=AFS;'
    'UID=FSAUser2;'
    'PWD=password'
)

cursor = conn.cursor()

# Check each commodity table for direction field
commodity_tables = {
    'RAW': 'RawInspectionRecordTypes',
    'PMP': 'ProcessedMeatInspectionRecord',
    'POULTRY': 'PoultryEggInspectionRecords',
}

for commodity, table_name in commodity_tables.items():
    print(f"\n{commodity} ({table_name}):")
    print("-" * 100)

    try:
        # Check total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]

        # Check how many have direction=True (1)
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE IsDirectionPresentForthisInspection = 1
        """)
        with_direction = cursor.fetchone()[0]

        # Check how many have direction=False (0)
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE IsDirectionPresentForthisInspection = 0
        """)
        without_direction = cursor.fetchone()[0]

        # Check for NULL values
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE IsDirectionPresentForthisInspection IS NULL
        """)
        null_direction = cursor.fetchone()[0]

        print(f"  Total: {total:,}")
        print(f"  With Direction (True): {with_direction:,} ({with_direction/total*100:.2f}%)")
        print(f"  Without Direction (False): {without_direction:,} ({without_direction/total*100:.2f}%)")
        print(f"  NULL values: {null_direction:,}")

        # Show sample records WITH direction
        if with_direction > 0:
            print(f"\n  Sample records WITH direction (first 5):")
            cursor.execute(f"""
                SELECT TOP 5 Id, DateOfInspection, Client, ProductName
                FROM {table_name}
                WHERE IsDirectionPresentForthisInspection = 1
                ORDER BY DateOfInspection DESC
            """)

            for row in cursor.fetchall():
                insp_id, date, client, product = row
                date_str = date.strftime('%Y-%m-%d') if date else 'N/A'
                client_name = (client or 'Unknown')[:30]
                product_name = (product or 'N/A')[:30]
                print(f"    {commodity}-{insp_id} | {date_str} | {client_name} | {product_name}")

    except Exception as e:
        print(f"  [ERROR] Could not query {table_name}: {e}")

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)

# Get totals across all tables
cursor.execute("""
    SELECT
        (SELECT COUNT(*) FROM RawInspectionRecordTypes WHERE IsDirectionPresentForthisInspection = 1) +
        (SELECT COUNT(*) FROM ProcessedMeatInspectionRecord WHERE IsDirectionPresentForthisInspection = 1) +
        (SELECT COUNT(*) FROM PoultryEggInspectionRecords WHERE IsDirectionPresentForthisInspection = 1) AS TotalWithDirection
""")
total_with_direction = cursor.fetchone()[0]

print(f"\nTotal inspections WITH direction across all commodities: {total_with_direction:,}")

if total_with_direction > 0:
    print("\n[ISSUE FOUND] SQL Server has inspections with directions,")
    print("but Django database shows 0. This is a sync problem!")
else:
    print("\n[INFO] SQL Server also shows 0 inspections with directions.")
    print("This means all inspections are actually compliant.")

conn.close()

print("=" * 100)
