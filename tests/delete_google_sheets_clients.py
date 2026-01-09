"""
Delete old Google Sheets clients, keep only SQL Server synced clients.
SQL Server clients have client_id starting with 'SQL-'
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Client

print("=" * 80)
print("DELETE OLD GOOGLE SHEETS CLIENTS")
print("=" * 80)

# Count current clients
total_clients = Client.objects.count()
sql_clients = Client.objects.filter(client_id__startswith='SQL-').count()
google_sheets_clients = Client.objects.exclude(client_id__startswith='SQL-').count()

print(f"\n[BEFORE] Client counts:")
print(f"  - Total clients: {total_clients}")
print(f"  - SQL Server clients (client_id starts with 'SQL-'): {sql_clients}")
print(f"  - Google Sheets clients (old data): {google_sheets_clients}")

print(f"\n[ACTION] Deleting {google_sheets_clients} Google Sheets clients...")

# Delete all clients that don't have 'SQL-' prefix
deleted_count = Client.objects.exclude(client_id__startswith='SQL-').delete()[0]

print(f"[OK] Deleted {deleted_count} Google Sheets clients")

# Count after deletion
total_after = Client.objects.count()
sql_after = Client.objects.filter(client_id__startswith='SQL-').count()

print(f"\n[AFTER] Client counts:")
print(f"  - Total clients: {total_after}")
print(f"  - SQL Server clients: {sql_after}")

print("\n" + "=" * 80)
print("[COMPLETE] Old Google Sheets clients removed!")
print("=" * 80)
print(f"\nHome page will now show: {total_after} Total Clients")
print("This matches the SQL Server database (active clients)")
print("=" * 80)
