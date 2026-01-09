import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

import pyodbc
from django.conf import settings

def check_clients_without_codes():
    """Find SQL Server clients without internal account codes"""

    # SQL Server connection
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

        # Query to find clients without internal account codes
        query = """
        SELECT
            Id,
            Name,
            InternalAccountNumber
        FROM Clients
        WHERE (InternalAccountNumber IS NULL
           OR InternalAccountNumber = ''
           OR LTRIM(RTRIM(InternalAccountNumber)) = '')
          AND IsActive = 1
        ORDER BY Name
        """

        print("Searching for active clients without internal account numbers...")
        print()

        cursor.execute(query)
        clients = cursor.fetchall()

        if not clients:
            print("All active clients have internal account numbers!")
            cursor.close()
            conn.close()
            return

        print(f"Found {len(clients)} active clients WITHOUT internal account numbers:")
        print("=" * 90)
        print(f"{'ID':<10} {'Client Name':<60} {'Internal Account Number':<20}")
        print("=" * 90)

        for client in clients:
            client_id = str(client.Id) or 'NULL'
            client_name = client.Name or 'NULL'
            internal_number = client.InternalAccountNumber or 'NULL'

            print(f"{client_id:<10} {client_name:<60} {internal_number:<20}")

        print("=" * 90)
        print(f"\nTotal active clients without internal account numbers: {len(clients)}")

        cursor.close()
        conn.close()

    except pyodbc.Error as e:
        print(f"SQL Server error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_clients_without_codes()
