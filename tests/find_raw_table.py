"""Find the correct RAW sample table name"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
import pymssql

sql_server_config = settings.DATABASES.get('sql_server', {})

connection = pymssql.connect(
    server=sql_server_config.get('HOST'),
    port=int(sql_server_config.get('PORT', 1433)),
    user=sql_server_config.get('USER'),
    password=sql_server_config.get('PASSWORD'),
    database=sql_server_config.get('NAME'),
    timeout=30
)
cursor = connection.cursor(as_dict=True)

print("Searching for tables with 'Raw' and 'Sample' or 'Lab' in the name...")
print()

cursor.execute("""
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
        AND TABLE_CATALOG = 'AFS'
        AND (
            (TABLE_NAME LIKE '%Raw%' AND (TABLE_NAME LIKE '%Sample%' OR TABLE_NAME LIKE '%Lab%'))
            OR TABLE_NAME LIKE '%RMP%Lab%'
            OR TABLE_NAME LIKE '%RMP%Sample%'
        )
    ORDER BY TABLE_NAME
""")

tables = cursor.fetchall()

if tables:
    print(f"Found {len(tables)} matching tables:")
    for table in tables:
        table_name = table['TABLE_NAME']
        print(f"\n  - {table_name}")

        # Try to get columns
        try:
            cursor.execute(f"SELECT TOP 1 * FROM AFS.dbo.{table_name}")
            result = cursor.fetchone()
            if result:
                cols = list(result.keys())
                print(f"    Columns: {', '.join(cols[:5])}" + ("..." if len(cols) > 5 else ""))

                # Check if it has the right columns
                if 'RawRMPInspectionRecordId' in cols or 'InspectionId' in cols:
                    print(f"    >>> THIS LOOKS LIKE THE RIGHT TABLE! <<<")
        except Exception as e:
            print(f"    Error reading table: {e}")
else:
    print("No matching tables found")

connection.close()
