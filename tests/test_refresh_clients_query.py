import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

import pyodbc
from django.conf import settings

def test_refresh_clients_query():
    """Test the refresh_clients SQL query"""

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

        print("Testing the refresh_clients query...")
        print()

        # This is the exact query from refresh_clients view
        query = """
            SELECT
                c.Id,
                c.Name,
                c.InternalAccountNumber,
                c.ContactNumber,
                c.ContactEmail,
                c.ContactNumberForInspections,
                c.ContactEmailForInspections,
                c.SiteName,
                c.PhysicalAddress,
                c.IsActive,
                CASE
                    WHEN c.ProvinceStateId = 1 THEN 'Eastern Cape'
                    WHEN c.ProvinceStateId = 2 THEN 'Gauteng'
                    WHEN c.ProvinceStateId = 3 THEN 'KwaZulu-Natal'
                    WHEN c.ProvinceStateId = 4 THEN 'Limpopo'
                    WHEN c.ProvinceStateId = 5 THEN 'Mpumalanga'
                    WHEN c.ProvinceStateId = 6 THEN 'Northern Cape'
                    WHEN c.ProvinceStateId = 7 THEN 'North West'
                    WHEN c.ProvinceStateId = 8 THEN 'Western Cape'
                    WHEN c.ProvinceStateId = 9 THEN 'Free State'
                    ELSE 'Unknown'
                END AS Province
            FROM Clients c
            WHERE c.IsActive = 1
            ORDER BY c.Id
        """

        print("Executing query...")
        cursor.execute(query)

        print("Fetching results...")
        results = cursor.fetchall()

        print(f"\nSUCCESS! Query returned {len(results)} active clients")
        print()

        # Show first 5 results
        print("Sample results (first 5):")
        print("=" * 150)
        print(f"{'ID':<10} {'Name':<40} {'Account Code':<20} {'Province':<20} {'Phone':<15}")
        print("=" * 150)

        for i, row in enumerate(results[:5]):
            client_id = row[0]
            name = (row[1] or 'NULL')[:40]
            account_code = (row[2] or 'NULL')[:20]
            province = (row[10] or 'NULL')[:20]
            phone = (row[3] or row[5] or 'NULL')[:15]

            print(f"{client_id:<10} {name:<40} {account_code:<20} {province:<20} {phone:<15}")

        print("=" * 150)

        cursor.close()
        conn.close()

    except pyodbc.Error as e:
        print(f"SQL Server error: {e}")
        print()
        print("Full error details:")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Full error details:")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_refresh_clients_query()
