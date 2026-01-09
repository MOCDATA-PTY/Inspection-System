"""
Find the correct direction table names in SQL Server
"""
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

print("=" * 100)
print("SEARCHING FOR DIRECTION/DIRECTIVE TABLES")
print("=" * 100)

# Search for tables with 'Direction' or 'Directive' in the name
cursor.execute("""
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
        AND TABLE_CATALOG = 'AFS'
        AND (TABLE_NAME LIKE '%Direction%' OR TABLE_NAME LIKE '%Directive%')
    ORDER BY TABLE_NAME
""")

tables = cursor.fetchall()

if tables:
    print(f"\nFound {len(tables)} direction/directive tables:\n")
    for table in tables:
        table_name = table['TABLE_NAME']
        print(f"  • {table_name}")

        # Try to get columns and sample data
        try:
            cursor.execute(f"SELECT TOP 1 * FROM AFS.dbo.{table_name}")
            result = cursor.fetchone()
            if result:
                cols = list(result.keys())
                # Look for foreign key columns
                fk_cols = [c for c in cols if 'InspectionRecord' in c or 'Inspection' in c]
                if fk_cols:
                    print(f"    FK columns: {', '.join(fk_cols)}")
        except Exception as e:
            print(f"    Error reading: {e}")
else:
    print("\nNo direction/directive tables found")

connection.close()
