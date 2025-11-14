"""
Test SQL Server connection using pymssql - NO ODBC DRIVERS NEEDED!
"""

import pymssql

print("=" * 80)
print("Testing SQL Server Connection with pymssql (NO ODBC DRIVERS!)")
print("=" * 80)

try:
    # Connect to SQL Server using pymssql
    print("\nConnecting to SQL Server...")
    conn = pymssql.connect(
        server='102.67.140.12',
        port=1053,
        user='FSAUser2',
        password='password',
        database='AFS',
        timeout=10
    )

    print("SUCCESS - Connection successful!")

    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()[0]
    print(f"\nSQL Server version:")
    print(f"  {version[:100]}...")

    # Test product query
    cursor.execute("""
        SELECT TOP 5 PMPItemDetails
        FROM PMPInspectedProductRecordTypes
        WHERE PMPItemDetails IS NOT NULL AND PMPItemDetails != ''
    """)

    print("\nSample product names:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}")

    cursor.close()
    conn.close()

    print("\n" + "=" * 80)
    print("SUCCESS - pymssql works PERFECTLY - NO ODBC DRIVERS NEEDED!")
    print("=" * 80)

except Exception as e:
    print(f"\nERROR - Connection failed: {e}")
    print("\nThis might be a firewall or network issue, not a driver issue.")
