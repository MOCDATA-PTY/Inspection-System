import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

import pyodbc
from django.conf import settings

def check_missing_in_sql():
    """Check if these clients exist in SQL Server"""

    clients_to_find = [
        "Checkers Dada Complex Lichtenburg",
        "Grootboom Slaghuis",
        "Superspar Mini Market",
        "Enkomeni Butchery",
        "Frank's Meat at Mall/N4",
        "Jwayelani Warwick",
        "Lester's Meat East London"
    ]

    sql_server_config = settings.DATABASES.get('sql_server', {})
    if not sql_server_config:
        print("SQL Server configuration not found")
        return

    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={sql_server_config['HOST']},{sql_server_config['PORT']};"
            f"DATABASE={sql_server_config['NAME']};"
            f"UID={sql_server_config['USER']};"
            f"PWD={sql_server_config['PASSWORD']}"
        )

        print("Connecting to SQL Server...")
        print()

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        print("Searching SQL Server for missing clients...")
        print("=" * 120)
        print(f"{'Client Name (Django)':<50} {'Found in SQL?':<15} {'SQL Server Name':<40} {'SQL Account Number':<15}")
        print("=" * 120)

        for client_name in clients_to_find:
            # Search for client in SQL Server
            query = """
            SELECT
                Id,
                Name,
                InternalAccountNumber,
                IsActive
            FROM Clients
            WHERE Name LIKE ?
            """

            cursor.execute(query, f'%{client_name}%')
            sql_results = cursor.fetchall()

            if sql_results:
                for sql_client in sql_results:
                    sql_name = sql_client.Name or 'NULL'
                    sql_code = sql_client.InternalAccountNumber or 'MISSING'
                    is_active = 'Active' if sql_client.IsActive else 'Inactive'

                    print(f"{client_name:<50} YES ({is_active}){'':<6} {sql_name:<40} {sql_code:<15}")
            else:
                print(f"{client_name:<50} NO{'':<13} {'-':<40} {'-':<15}")

        print("=" * 120)

        cursor.close()
        conn.close()

    except pyodbc.Error as e:
        print(f"SQL Server error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_missing_in_sql()
