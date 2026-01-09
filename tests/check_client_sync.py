"""
Check client synchronization status and count from SQL Server
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import SQLServerConnection
from main.models import ClientAllocation

print("="*80)
print("CLIENT SYNCHRONIZATION STATUS CHECK")
print("="*80)

# Check Django database
django_count = ClientAllocation.objects.count()
active_count = ClientAllocation.objects.filter(active_status='Active').count()
inactive_count = ClientAllocation.objects.filter(active_status='Inactive').count()

print(f"\nDjango Database (PostgreSQL):")
print(f"  Total clients: {django_count}")
print(f"  Active: {active_count}")
print(f"  Inactive: {inactive_count}")

# Check SQL Server
try:
    sql_conn = SQLServerConnection()
    cursor = sql_conn.connection.cursor()

    # Count all clients
    cursor.execute("SELECT COUNT(*) FROM Clients")
    total_sql = cursor.fetchone()[0]

    # Count active clients
    cursor.execute("SELECT COUNT(*) FROM Clients WHERE IsActive = 1")
    active_sql = cursor.fetchone()[0]

    # Count inactive clients
    cursor.execute("SELECT COUNT(*) FROM Clients WHERE IsActive = 0")
    inactive_sql = cursor.fetchone()[0]

    print(f"\nSQL Server Database:")
    print(f"  Total clients: {total_sql}")
    print(f"  Active (IsActive=1): {active_sql}")
    print(f"  Inactive (IsActive=0): {inactive_sql}")

    # Check for duplicates in SQL Server
    cursor.execute("""
        SELECT Name, COUNT(*) as count
        FROM Clients
        WHERE IsActive = 1
        GROUP BY Name
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """)
    duplicates = cursor.fetchall()

    if duplicates:
        print(f"\n[WARNING] Found {len(duplicates)} duplicate client names in SQL Server:")
        for i, (name, count) in enumerate(duplicates[:10], 1):
            print(f"  {i}. '{name}' appears {count} times")
        if len(duplicates) > 10:
            print(f"  ... and {len(duplicates) - 10} more")

    # Check for duplicate IDs in SQL Server
    cursor.execute("""
        SELECT Id, COUNT(*) as count
        FROM Clients
        WHERE IsActive = 1
        GROUP BY Id
        HAVING COUNT(*) > 1
    """)
    id_duplicates = cursor.fetchall()

    if id_duplicates:
        print(f"\n[WARNING] Found {len(id_duplicates)} duplicate client IDs in SQL Server")

    sql_conn.close()

    # Show sync difference
    print(f"\n" + "="*80)
    print("SYNC ANALYSIS:")
    print("="*80)

    difference = active_sql - django_count

    if difference > 0:
        print(f"\n[ALERT] {difference} clients in SQL Server are NOT in Django database")
        print(f"  SQL Server active clients: {active_sql}")
        print(f"  Django total clients: {django_count}")
        print(f"\n  Recommendation: Run the sync to update Django database")
    elif difference < 0:
        print(f"\n[INFO] Django has {abs(difference)} more clients than SQL Server active clients")
        print(f"  This may be due to manually added clients or different sync timing")
    else:
        print(f"\n[OK] Client counts match! Both have {active_sql} clients")

    if inactive_sql > 0:
        print(f"\n[INFO] {inactive_sql} inactive clients in SQL Server are not being synced")
        print(f"  (This is expected behavior - only active clients are synced)")

except Exception as e:
    print(f"\n[ERROR] Could not connect to SQL Server: {e}")
    print(f"  Using Django database count only")

print(f"\n" + "="*80)
print("RECOMMENDATION:")
print("="*80)

if 'difference' in locals() and difference > 0:
    print("\nTo sync the latest clients from SQL Server, run:")
    print("  python manage.py shell")
    print("  >>> from main.services.scheduled_sync_service import ScheduledSyncService")
    print("  >>> service = ScheduledSyncService()")
    print("  >>> service.sync_sql_server_clients()")
    print(f"\nThis will import all {active_sql} active clients from SQL Server")
else:
    print("\nClient data appears to be in sync. No action needed.")

print("="*80)
