"""
Test script to diagnose client-shipment relationship issues.

Run this with: python test.py

This will show:
1. All clients in database
2. All shipments and their client links
3. Orphaned shipments (no client)
4. Clients with no shipments
5. Specific date filtering
6. Mismatches and issues
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Client, Shipment
from django.db.models import Count
import datetime

print("=" * 80)
print("CLIENT-SHIPMENT RELATIONSHIP DIAGNOSTIC")
print("=" * 80)

# ============================================
# 1. DATABASE OVERVIEW
# ============================================
print("\n" + "=" * 80)
print("1. DATABASE OVERVIEW")
print("=" * 80)

total_clients = Client.objects.count()
total_shipments = Shipment.objects.count()
shipments_with_client = Shipment.objects.filter(client__isnull=False).count()
shipments_without_client = Shipment.objects.filter(client__isnull=True).count()

print(f"\nTotal Clients:              {total_clients}")
print(f"Total Shipments:            {total_shipments}")
print(f"Shipments WITH client:      {shipments_with_client}")
print(f"Shipments WITHOUT client:   {shipments_without_client}")

if shipments_without_client > 0:
    print(f"\n⚠️  WARNING: {shipments_without_client} shipments have NO client assigned!")

# ============================================
# 2. ALL CLIENTS
# ============================================
print("\n" + "=" * 80)
print("2. ALL CLIENTS IN DATABASE")
print("=" * 80)

clients = Client.objects.all().order_by('name')

if clients.exists():
    print(f"\n{'ID':<5} {'Client ID':<12} {'Account Code':<15} {'Name':<40} {'Shipments':<10}")
    print("-" * 85)
    
    for client in clients:
        shipment_count = Shipment.objects.filter(client=client).count()
        account_code = client.internal_account_code or "N/A"
        
        print(f"{client.id:<5} {client.client_id:<12} {account_code:<15} {client.name[:38]:<40} {shipment_count:<10}")
else:
    print("\n⚠️  NO CLIENTS FOUND IN DATABASE!")

# ============================================
# 3. CLIENTS WITH NO SHIPMENTS
# ============================================
print("\n" + "=" * 80)
print("3. CLIENTS WITH NO SHIPMENTS")
print("=" * 80)

clients_no_shipments = Client.objects.annotate(
    num_shipments=Count('shipments')
).filter(num_shipments=0)

if clients_no_shipments.exists():
    print(f"\n⚠️  Found {clients_no_shipments.count()} clients with NO shipments:\n")
    for client in clients_no_shipments:
        account_code = client.internal_account_code or "N/A"
        print(f"  • {client.name} (ID: {client.client_id}, Account: {account_code})")
else:
    print("\n✓ All clients have at least one shipment")

# ============================================
# 4. ORPHANED SHIPMENTS (NO CLIENT)
# ============================================
print("\n" + "=" * 80)
print("4. ORPHANED SHIPMENTS (NO CLIENT ASSIGNED)")
print("=" * 80)

orphaned_shipments = Shipment.objects.filter(client__isnull=True)

if orphaned_shipments.exists():
    print(f"\n⚠️  Found {orphaned_shipments.count()} orphaned shipments:\n")
    print(f"{'Claim No':<15} {'Branch':<10} {'Intend Date':<15} {'Status':<10}")
    print("-" * 50)
    
    for shipment in orphaned_shipments[:20]:  # Show first 20
        intend_date = shipment.Intend_Claim_Date.strftime("%Y-%m-%d") if shipment.Intend_Claim_Date else "N/A"
        status = shipment.Formal_Claim_Received or "N/A"
        
        print(f"{shipment.Claim_No:<15} {shipment.Branch:<10} {intend_date:<15} {status:<10}")
    
    if orphaned_shipments.count() > 20:
        print(f"\n... and {orphaned_shipments.count() - 20} more")
else:
    print("\n✓ No orphaned shipments found")

# ============================================
# 5. RECENT SHIPMENTS (NOVEMBER 2024)
# ============================================
print("\n" + "=" * 80)
print("5. SHIPMENTS FROM NOVEMBER 2024")
print("=" * 80)

# Check for November 2024 shipments
november_start = datetime.date(2024, 11, 1)
november_end = datetime.date(2024, 11, 30)

november_shipments = Shipment.objects.filter(
    Intend_Claim_Date__gte=november_start,
    Intend_Claim_Date__lte=november_end
).order_by('Intend_Claim_Date')

print(f"\nFound {november_shipments.count()} shipments in November 2024:\n")

if november_shipments.exists():
    print(f"{'Date':<12} {'Claim No':<15} {'Client Name':<40} {'Has Client?':<12}")
    print("-" * 85)
    
    for shipment in november_shipments:
        date = shipment.Intend_Claim_Date.strftime("%Y-%m-%d") if shipment.Intend_Claim_Date else "N/A"
        claim_no = shipment.Claim_No
        
        if shipment.client:
            client_name = shipment.client.name[:38]
            has_client = "✓ Yes"
        else:
            client_name = "⚠️  NO CLIENT ASSIGNED"
            has_client = "✗ No"
        
        print(f"{date:<12} {claim_no:<15} {client_name:<40} {has_client:<12}")
else:
    print("No shipments found for November 2024")

# ============================================
# 6. SPECIFIC DATE CHECK (November 5, 2024)
# ============================================
print("\n" + "=" * 80)
print("6. SHIPMENTS ON NOVEMBER 5, 2024")
print("=" * 80)

november_5 = datetime.date(2024, 11, 5)

nov5_shipments = Shipment.objects.filter(
    Intend_Claim_Date=november_5
) | Shipment.objects.filter(
    Formal_Claim_Date_Received=november_5
)

if nov5_shipments.exists():
    print(f"\nFound {nov5_shipments.count()} shipment(s) on November 5, 2024:\n")
    
    for shipment in nov5_shipments:
        print(f"\n  Claim No: {shipment.Claim_No}")
        print(f"  Branch: {shipment.Branch}")
        print(f"  Intend Date: {shipment.Intend_Claim_Date}")
        print(f"  Formal Date: {shipment.Formal_Claim_Date_Received}")
        
        if shipment.client:
            print(f"  ✓ Client: {shipment.client.name}")
            print(f"    Client ID: {shipment.client.client_id}")
            print(f"    Account Code: {shipment.client.internal_account_code or 'N/A'}")
        else:
            print(f"  ✗ NO CLIENT ASSIGNED!")
        
        print("-" * 50)
else:
    print("\nNo shipments found on November 5, 2024")

# ============================================
# 7. CLIENT BREAKDOWN WITH SHIPMENT DETAILS
# ============================================
print("\n" + "=" * 80)
print("7. DETAILED CLIENT BREAKDOWN (Clients with shipments)")
print("=" * 80)

clients_with_shipments = Client.objects.annotate(
    num_shipments=Count('shipments')
).filter(num_shipments__gt=0).order_by('-num_shipments')

print(f"\nShowing top 20 clients by shipment count:\n")

if clients_with_shipments.exists():
    print(f"{'Client Name':<40} {'Account Code':<15} {'Shipments':<10} {'Latest Date':<12}")
    print("-" * 80)
    
    for client in clients_with_shipments[:20]:
        # Get latest shipment date
        latest_shipment = Shipment.objects.filter(client=client).order_by('-Intend_Claim_Date').first()
        latest_date = latest_shipment.Intend_Claim_Date.strftime("%Y-%m-%d") if latest_shipment and latest_shipment.Intend_Claim_Date else "N/A"
        
        account_code = client.internal_account_code or "N/A"
        
        print(f"{client.name[:38]:<40} {account_code:<15} {client.num_shipments:<10} {latest_date:<12}")
else:
    print("\nNo clients with shipments found")

# ============================================
# 8. POTENTIAL ISSUES SUMMARY
# ============================================
print("\n" + "=" * 80)
print("8. POTENTIAL ISSUES SUMMARY")
print("=" * 80)

issues = []

if shipments_without_client > 0:
    issues.append(f"⚠️  {shipments_without_client} shipments have NO client assigned")

if clients_no_shipments.count() > 0:
    issues.append(f"⚠️  {clients_no_shipments.count()} clients have NO shipments")

# Check for duplicate client names
duplicate_names = Client.objects.values('name').annotate(
    count=Count('id')
).filter(count__gt=1)

if duplicate_names.exists():
    issues.append(f"⚠️  {duplicate_names.count()} duplicate client names found")

# Check for clients without account codes
no_account_code = Client.objects.filter(internal_account_code__isnull=True) | Client.objects.filter(internal_account_code='')
if no_account_code.exists():
    issues.append(f"⚠️  {no_account_code.count()} clients have NO account code")

if issues:
    print("\nISSUES FOUND:\n")
    for issue in issues:
        print(f"  {issue}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    
    if shipments_without_client > 0:
        print("\n1. Fix orphaned shipments:")
        print("   - Manually assign clients to shipments without clients")
        print("   - Or run a script to match by legacy client name field")
    
    if clients_no_shipments.count() > 0:
        print("\n2. Clean up unused clients:")
        print("   - Review clients with no shipments")
        print("   - Delete if they're not needed")
    
    if duplicate_names.exists():
        print("\n3. Merge duplicate clients:")
        print("   - Find clients with same name")
        print("   - Merge them into one client")
        print("   - Reassign shipments to merged client")
    
    if no_account_code.exists():
        print("\n4. Add account codes:")
        print("   - Ensure all clients have internal_account_code")
        print("   - This is needed for reliable Google Sheets sync")

else:
    print("\n✓ NO ISSUES FOUND!")
    print("\nYour database looks good:")
    print("  • All shipments have clients")
    print("  • All clients have shipments")
    print("  • No duplicates detected")

# ============================================
# 9. SEARCH FOR SPECIFIC CLIENT
# ============================================
print("\n" + "=" * 80)
print("9. SEARCH FOR SPECIFIC CLIENT (INTERACTIVE)")
print("=" * 80)

print("\nEnter a client name to search (or press Enter to skip):")
search_term = input("> ").strip()

if search_term:
    matching_clients = Client.objects.filter(name__icontains=search_term)
    
    if matching_clients.exists():
        print(f"\nFound {matching_clients.count()} matching client(s):\n")
        
        for client in matching_clients:
            print(f"\n  Client: {client.name}")
            print(f"  Client ID: {client.client_id}")
            print(f"  Account Code: {client.internal_account_code or 'N/A'}")
            print(f"  Email: {client.email or 'N/A'}")
            
            shipments = Shipment.objects.filter(client=client).order_by('-Intend_Claim_Date')
            print(f"  Shipments: {shipments.count()}")
            
            if shipments.exists():
                print(f"\n  Recent shipments:")
                for shipment in shipments[:5]:
                    date = shipment.Intend_Claim_Date.strftime("%Y-%m-%d") if shipment.Intend_Claim_Date else "N/A"
                    print(f"    • {shipment.Claim_No} - {date} - {shipment.Branch}")
                
                if shipments.count() > 5:
                    print(f"    ... and {shipments.count() - 5} more")
            
            print("-" * 50)
    else:
        print(f"\n✗ No clients found matching '{search_term}'")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)