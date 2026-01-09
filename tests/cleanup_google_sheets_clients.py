"""
CLEANUP: Remove old Google Sheets clients from Client table
This will leave ONLY SQL Server synced clients

WARNING: This will delete 4,977 client records that came from Google Sheets!
Only run this if you're sure you want to remove the Google Sheets data.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Client

print("="*80)
print("CLEANUP PREVIEW - Google Sheets Clients")
print("="*80)

# Count clients
total_clients = Client.objects.count()
sql_clients = Client.objects.filter(client_id__startswith='SQL-').count()
google_sheets_clients = Client.objects.exclude(client_id__startswith='SQL-').count()

print(f"\nCurrent state:")
print(f"  Total clients: {total_clients:,}")
print(f"  SQL Server clients: {sql_clients:,}")
print(f"  Google Sheets clients: {google_sheets_clients:,}")

print(f"\n" + "="*80)
print("WARNING: This script will DELETE Google Sheets clients!")
print("="*80)

print(f"\nAfter cleanup:")
print(f"  Total clients: {sql_clients:,} (SQL Server only)")
print(f"  Clients deleted: {google_sheets_clients:,}")

# Ask for confirmation
print(f"\n" + "="*80)
response = input("Type 'DELETE' to proceed with cleanup (or anything else to cancel): ")

if response == 'DELETE':
    print("\nDeleting Google Sheets clients...")
    deleted_count = Client.objects.exclude(client_id__startswith='SQL-').delete()[0]

    print(f"[OK] Deleted {deleted_count:,} Google Sheets clients")

    remaining = Client.objects.count()
    print(f"[OK] Remaining clients: {remaining:,} (all from SQL Server)")

    print(f"\n" + "="*80)
    print("[SUCCESS] Cleanup completed!")
    print(f"Home page will now show: {remaining:,} Total Clients")
    print("="*80)
else:
    print("\n[CANCELLED] No changes made.")
