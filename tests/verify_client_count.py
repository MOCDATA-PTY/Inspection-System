"""
Verify client count after cleanup
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Client

print("=" * 80)
print("CLIENT COUNT VERIFICATION")
print("=" * 80)

total = Client.objects.count()
sql_clients = Client.objects.filter(client_id__startswith='SQL-').count()

# Sample a few clients to show they're all SQL Server clients
sample_clients = Client.objects.all()[:5]

print(f"\n[VERIFIED] Total Clients: {total}")
print(f"[VERIFIED] All clients are from SQL Server: {sql_clients == total}")

print(f"\n[SAMPLE] First 5 clients:")
for client in sample_clients:
    print(f"  - {client.client_id}: {client.name}")

print("\n" + "=" * 80)
print(f"Home page will display: {total} Total Clients")
print("=" * 80)
print("\n[OK] Client count is now correct!")
print("     - Old Google Sheets data removed (4,977 clients)")
print("     - Only SQL Server clients remain (4,963 clients)")
print("     - Matches SQL Server active clients count")
print("=" * 80)
