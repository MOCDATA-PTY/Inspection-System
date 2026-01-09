import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Client

def check_django_clients_without_codes():
    """Find Django clients without internal account codes"""

    print("Checking Django PostgreSQL database for clients without internal account codes...")
    print()

    # Query clients without internal account codes
    clients_without_codes = Client.objects.filter(
        internal_account_code__isnull=True
    ) | Client.objects.filter(
        internal_account_code=''
    )

    clients_without_codes = clients_without_codes.order_by('client_name')

    if not clients_without_codes.exists():
        print("All Django clients have internal account codes!")
        return

    print(f"Found {clients_without_codes.count()} Django clients WITHOUT internal account codes:")
    print("=" * 100)
    print(f"{'ID':<10} {'Client Name':<50} {'Source':<15} {'Internal Account Code':<25}")
    print("=" * 100)

    for client in clients_without_codes:
        client_id = str(client.id)
        client_name = client.new_client_name or 'NULL'
        source = client.source or 'NULL'
        internal_code = client.internal_account_code or 'NULL'

        print(f"{client_id:<10} {client_name:<50} {source:<15} {internal_code:<25}")

    print("=" * 100)
    print(f"\nTotal Django clients without internal account codes: {clients_without_codes.count()}")

    # Check if these clients exist in SQL Server
    print("\n" + "=" * 100)
    print("Checking if these clients should have codes from SQL Server...")
    print("=" * 100)

    sql_server_clients = clients_without_codes.filter(source='sql_server')
    google_sheets_clients = clients_without_codes.filter(source='google_sheets')

    print(f"\nFrom SQL Server: {sql_server_clients.count()} clients")
    print(f"From Google Sheets: {google_sheets_clients.count()} clients")

    if sql_server_clients.exists():
        print("\nSQL Server clients without codes (these should have codes!):")
        print("=" * 100)
        for client in sql_server_clients:
            print(f"  - {client.new_client_name} (ID: {client.id})")
        print("=" * 100)

if __name__ == '__main__':
    check_django_clients_without_codes()
