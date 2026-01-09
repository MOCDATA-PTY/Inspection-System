"""
Compare Client vs ClientAllocation model counts
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Client, ClientAllocation

print("="*80)
print("CLIENT MODEL COMPARISON")
print("="*80)

# Count Client model (used on home page)
client_count = Client.objects.count()

# Count ClientAllocation model (used in sync scripts)
client_allocation_count = ClientAllocation.objects.count()

print(f"\nClient model count: {client_count:,}")
print(f"ClientAllocation model count: {client_allocation_count:,}")
print(f"Difference: {abs(client_count - client_allocation_count):,}")

if client_count == 4977:
    print(f"\n[FOUND] Client.objects.count() = 4,977 (matches home page display!)")
else:
    print(f"\n[INFO] Client.objects.count() = {client_count:,}")

if client_allocation_count == 4964:
    print(f"[FOUND] ClientAllocation.objects.count() = 4,964 (matches our previous count!)")
else:
    print(f"[INFO] ClientAllocation.objects.count() = {client_allocation_count:,}")

print("\n" + "="*80)
print("EXPLANATION:")
print("="*80)
print("The home page uses Client.objects.count() which is showing", client_count)
print("The sync scripts use ClientAllocation.objects.count() which is showing", client_allocation_count)
print("These are TWO DIFFERENT TABLES in the database!")
print("="*80)
