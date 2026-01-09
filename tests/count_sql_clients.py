"""
Count total clients in SQL Server (both active and inactive)
This script only COUNTS - it does NOT import or sync anything
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import SQLServerConnection
from main.models import ClientAllocation

print("="*80)
print("SQL SERVER CLIENT COUNT")
print("="*80)

try:
    # Connect to SQL Server
    sql_conn = SQLServerConnection()
    if not sql_conn.connect():
        raise Exception("Failed to connect to SQL Server")

    cursor = sql_conn.connection.cursor()

    print("\nQuerying SQL Server...")

    # Count ALL clients
    cursor.execute("SELECT COUNT(*) FROM Clients")
    total_sql = cursor.fetchone()[0]

    # Count ACTIVE clients (IsActive = 1)
    cursor.execute("SELECT COUNT(*) FROM Clients WHERE IsActive = 1")
    active_sql = cursor.fetchone()[0]

    # Count INACTIVE clients (IsActive = 0 or NULL)
    cursor.execute("SELECT COUNT(*) FROM Clients WHERE IsActive = 0 OR IsActive IS NULL")
    inactive_sql = cursor.fetchone()[0]

    print("\n" + "="*80)
    print("SQL SERVER (Source Database)")
    print("="*80)
    print(f"  Total clients: {total_sql:,}")
    print(f"  Active (IsActive=1): {active_sql:,}")
    print(f"  Inactive (IsActive=0): {inactive_sql:,}")

    # Check Django database
    django_total = ClientAllocation.objects.count()
    django_active = ClientAllocation.objects.filter(active_status='Active').count()
    django_inactive = ClientAllocation.objects.filter(active_status='Inactive').count()

    print("\n" + "="*80)
    print("DJANGO DATABASE (Application)")
    print("="*80)
    print(f"  Total clients: {django_total:,}")
    print(f"  Active: {django_active:,}")
    print(f"  Inactive: {django_inactive:,}")

    # Compare
    print("\n" + "="*80)
    print("SYNC STATUS")
    print("="*80)

    difference = active_sql - django_total

    if difference > 0:
        print(f"\n  SQL Server has {difference:,} MORE active clients than Django")
        print(f"  Recommendation: Run sync to update Django database")
    elif difference < 0:
        print(f"\n  Django has {abs(difference):,} MORE clients than SQL Server active clients")
        print(f"  (This may include manually added clients)")
    else:
        print(f"\n  [OK] Sync is up to date! Both have {active_sql:,} clients")

    if inactive_sql > 0:
        print(f"\n  Note: {inactive_sql:,} inactive clients in SQL Server are NOT being synced")
        print(f"        (This is expected - only active clients are synced)")

    sql_conn.disconnect()

    print("\n" + "="*80)

except Exception as e:
    print(f"\n[ERROR] Could not connect to SQL Server: {e}")
    print("\nPlease check:")
    print("  1. SQL Server is running and accessible")
    print("  2. Connection credentials are configured in settings")
    import traceback
    traceback.print_exc()
