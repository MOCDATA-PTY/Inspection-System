"""
Script to check the AFS Clients table structure and sample data
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import connections

def check_afs_clients_table():
    """Check the AFS Clients table"""

    print("=" * 80)
    print("AFS Clients Table Analysis")
    print("=" * 80)

    try:
        with connections['afs'].cursor() as cursor:
            # Get table structure
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'Clients'
                ORDER BY ORDINAL_POSITION
            """)

            print("\n[TABLE STRUCTURE]")
            print("-" * 80)
            columns_info = cursor.fetchall()

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
            for i, row in enumerate(rows, 1):
                print(f"\nRecord {i}:")
                for col, val in zip(columns, row):
                    print(f"  {col:30} = {val}")

            # Get total count
            cursor.execute("SELECT COUNT(*) FROM Clients")
            total_count = cursor.fetchone()[0]

            print("\n" + "=" * 80)
            print(f"Total records in Clients table: {total_count}")
            print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] Failed to query AFS Clients table: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_afs_clients_table()
