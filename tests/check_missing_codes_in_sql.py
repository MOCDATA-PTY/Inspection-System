import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

import pyodbc
from django.conf import settings
from main.models import Client

def check_missing_codes_in_sql():
    """Check if Django clients without codes exist in SQL Server"""

    print("Step 1: Finding Django clients without internal account codes...")
    print()

    # Get Django clients without codes
    django_clients = Client.objects.filter(
        internal_account_code__isnull=True
    ) | Client.objects.filter(
        internal_account_code=''
    )
    django_clients = django_clients.order_by('name')

    if not django_clients.exists():
        print("All Django clients have internal account codes!")
        return

    print(f"Found {django_clients.count()} Django clients WITHOUT codes")
    print()

    # Connect to SQL Server
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

        print("Step 2: Connecting to SQL Server to check for these clients...")
        print(f"Server: {sql_server_config['HOST']}:{sql_server_config['PORT']}")
        print()

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        print("Step 3: Searching SQL Server for each Django client...")
        print("=" * 120)
        print(f"{'Django Client Name':<50} {'Found in SQL?':<15} {'SQL Server Name':<35} {'SQL Account Code':<20}")
        print("=" * 120)

        found_count = 0
        not_found_count = 0
        found_with_code = 0
        found_without_code = 0

        for django_client in django_clients:
            client_name = django_client.name

            # Search for client in SQL Server by name
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
                found_count += 1
                for sql_client in sql_results:
                    sql_name = sql_client.Name or 'NULL'
                    sql_code = sql_client.InternalAccountNumber or 'MISSING'
                    is_active = 'Active' if sql_client.IsActive else 'Inactive'

                    if sql_code != 'MISSING':
                        found_with_code += 1
                        status = f"YES ({is_active})"
                    else:
                        found_without_code += 1
                        status = f"YES ({is_active})"

                    print(f"{client_name:<50} {status:<15} {sql_name:<35} {sql_code:<20}")
            else:
                not_found_count += 1
                print(f"{client_name:<50} {'NO':<15} {'-':<35} {'-':<20}")

        print("=" * 120)
        print()
        print("SUMMARY:")
        print(f"  Total Django clients without codes: {django_clients.count()}")
        print(f"  Found in SQL Server: {found_count}")
        print(f"    - With account codes in SQL: {found_with_code}")
        print(f"    - Without account codes in SQL: {found_without_code}")
        print(f"  NOT found in SQL Server: {not_found_count}")
        print()

        if found_with_code > 0:
            print(f"ACTION NEEDED: {found_with_code} clients exist in SQL Server WITH codes but are missing codes in Django!")
            print("These need to be synced from SQL Server.")

        cursor.close()
        conn.close()

    except pyodbc.Error as e:
        print(f"SQL Server error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_missing_codes_in_sql()
