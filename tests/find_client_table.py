import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

import pyodbc
from django.conf import settings

def find_client_table():
    """Find the correct client table name in SQL Server"""

    sql_server_config = settings.DATABASES.get('sql_server', {})

    if not sql_server_config:
        print("SQL Server configuration not found")
        return

    try:
        # Build connection string
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={sql_server_config['HOST']},{sql_server_config['PORT']};"
            f"DATABASE={sql_server_config['NAME']};"
            f"UID={sql_server_config['USER']};"
            f"PWD={sql_server_config['PASSWORD']}"
        )

        print(f"Connecting to SQL Server: {sql_server_config['HOST']}:{sql_server_config['PORT']}")
        print(f"Database: {sql_server_config['NAME']}")
        print()

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        # Query to find tables with 'Client' in the name
        query = """
        SELECT
            TABLE_SCHEMA,
            TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
          AND (TABLE_NAME LIKE '%Client%' OR TABLE_NAME LIKE '%Customer%')
        ORDER BY TABLE_NAME
        """

        print("Searching for client-related tables...")
        print()

        cursor.execute(query)
        tables = cursor.fetchall()

        if not tables:
            print("No client-related tables found")
        else:
            print(f"Found {len(tables)} client-related tables:")
            print("=" * 60)
            for table in tables:
                print(f"{table.TABLE_SCHEMA}.{table.TABLE_NAME}")
            print("=" * 60)

        # Also get columns from the first table
        if tables:
            first_table = f"{tables[0].TABLE_SCHEMA}.{tables[0].TABLE_NAME}"
            print(f"\nColumns in {first_table}:")
            print("=" * 60)

            col_query = f"""
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{tables[0].TABLE_SCHEMA}'
              AND TABLE_NAME = '{tables[0].TABLE_NAME}'
            ORDER BY ORDINAL_POSITION
            """

            cursor.execute(col_query)
            columns = cursor.fetchall()

            for col in columns:
                nullable = "NULL" if col.IS_NULLABLE == "YES" else "NOT NULL"
                print(f"  {col.COLUMN_NAME:<40} {col.DATA_TYPE:<20} {nullable}")
            print("=" * 60)

        cursor.close()
        conn.close()

    except pyodbc.Error as e:
        print(f"SQL Server error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    find_client_table()
