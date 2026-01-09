"""
Script to check the SQL Server Clients table
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import SQLServerConnection

def check_clients_table():
    """Check the SQL Server Clients table"""

    print("=" * 80)
    print("SQL Server Clients Table Analysis")
    print("=" * 80)

    conn = SQLServerConnection()

    if not conn.connect():
        print("\n[ERROR] Failed to connect to SQL Server")
        return

    try:
        cursor = conn.connection.cursor()

        # Get table structure
        print("\n[TABLE STRUCTURE]")
        print("-" * 80)

        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'Clients'
            ORDER BY ORDINAL_POSITION
        """)

        columns_info = cursor.fetchall()

        if not columns_info:
            print("  [WARNING] No table structure found. Table may not exist or may be in a different schema.")

            # Try to find tables with similar names
            cursor.execute("""
                SELECT TABLE_SCHEMA, TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME LIKE '%Client%'
            """)

            similar_tables = cursor.fetchall()
            if similar_tables:
                print("\n  Tables with similar names:")
                for schema, table in similar_tables:
                    print(f"    - {schema}.{table}")
        else:
            for col_name, data_type, max_length, is_nullable in columns_info:
                length_str = f"({max_length})" if max_length else ""
                nullable_str = "NULL" if is_nullable == 'YES' else "NOT NULL"
                print(f"  {col_name:30} {data_type}{length_str:15} {nullable_str}")

            # Get sample data
            cursor.execute("SELECT TOP 5 * FROM Clients")
            columns = [col[0] for col in cursor.description]

            print("\n[SAMPLE DATA - First 5 records]")
            print("-" * 80)

            rows = cursor.fetchall()
            if rows:
                for i, row in enumerate(rows, 1):
                    print(f"\nRecord {i}:")
                    for col, val in zip(columns, row):
                        print(f"  {col:30} = {val}")
            else:
                print("  No data found in table")

            # Get total count
            cursor.execute("SELECT COUNT(*) FROM Clients")
            total_count = cursor.fetchone()[0]

            print("\n" + "=" * 80)
            print(f"Total records in Clients table: {total_count}")
            print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] Failed to query Clients table: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        conn.disconnect()

if __name__ == '__main__':
    check_clients_table()
