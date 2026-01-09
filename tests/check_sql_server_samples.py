import pymssql

print("=" * 80)
print("FINDING AVAILABLE COLUMNS IN SQL SERVER PRODUCT TABLES")
print("=" * 80)

try:
    connection = pymssql.connect(
        server='102.67.140.12',
        port=1053,
        user='FSAUser2',
        password='password',
        database='AFS',
        timeout=30
    )

    cursor = connection.cursor(as_dict=True)

    # Check available columns in RAW product table
    print("\n" + "=" * 80)
    print("COLUMNS IN RawRMPInspectedProductRecordTypes")
    print("=" * 80)

    raw_columns_query = """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'RawRMPInspectedProductRecordTypes'
        AND COLUMN_NAME LIKE '%Sample%' OR COLUMN_NAME LIKE '%Fat%' OR COLUMN_NAME LIKE '%Protein%'
           OR COLUMN_NAME LIKE '%Test%' OR COLUMN_NAME LIKE '%Lab%'
        ORDER BY COLUMN_NAME
    """

    cursor.execute(raw_columns_query)
    raw_columns = cursor.fetchall()

    if raw_columns:
        print("\nSample/Test-related columns:")
        for col in raw_columns:
            print(f"  - {col['COLUMN_NAME']} ({col['DATA_TYPE']})")
    else:
        print("\nNo sample-related columns found. Showing ALL columns:")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'RawRMPInspectedProductRecordTypes'
            ORDER BY COLUMN_NAME
        """)
        all_cols = cursor.fetchall()
        for col in all_cols:
            print(f"  - {col['COLUMN_NAME']} ({col['DATA_TYPE']})")

    # Check available columns in PMP product table
    print("\n" + "=" * 80)
    print("COLUMNS IN PMPInspectedProductRecordTypes")
    print("=" * 80)

    pmp_columns_query = """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'PMPInspectedProductRecordTypes'
        AND COLUMN_NAME LIKE '%Sample%' OR COLUMN_NAME LIKE '%Fat%' OR COLUMN_NAME LIKE '%Protein%'
           OR COLUMN_NAME LIKE '%Test%' OR COLUMN_NAME LIKE '%Lab%'
        ORDER BY COLUMN_NAME
    """

    cursor.execute(pmp_columns_query)
    pmp_columns = cursor.fetchall()

    if pmp_columns:
        print("\nSample/Test-related columns:")
        for col in pmp_columns:
            print(f"  - {col['COLUMN_NAME']} ({col['DATA_TYPE']})")
    else:
        print("\nNo sample-related columns found. Showing ALL columns:")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'PMPInspectedProductRecordTypes'
            ORDER BY COLUMN_NAME
        """)
        all_cols = cursor.fetchall()
        for col in all_cols:
            print(f"  - {col['COLUMN_NAME']} ({col['DATA_TYPE']})")

    # Show sample data from RAW products
    print("\n" + "=" * 80)
    print("SAMPLE DATA FROM RECENT RAW PRODUCTS")
    print("=" * 80)

    cursor.execute("""
        SELECT TOP 5 *
        FROM AFS.dbo.RawRMPInspectedProductRecordTypes
        WHERE InspectionId IN (
            SELECT TOP 5 Id
            FROM AFS.dbo.RawRMPInspectionRecordTypes
            WHERE DateOfInspection >= '2025-12-01'
            AND IsActive = 1
            ORDER BY DateOfInspection DESC
        )
    """)
    raw_sample = cursor.fetchall()

    if raw_sample:
        print(f"\nShowing first product with all its columns:")
        first = raw_sample[0]
        for key, value in first.items():
            print(f"  {key}: {value}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
The IsSampleTaken column does NOT exist in SQL Server product tables.
We need to either:
1. Find a different column that indicates sample status
2. Derive is_sample_taken from test parameters (if Fat=TRUE, assume sampled)
3. Add the IsSampleTaken column to SQL Server source tables
""")
    print("=" * 80)

    cursor.close()
    connection.close()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
