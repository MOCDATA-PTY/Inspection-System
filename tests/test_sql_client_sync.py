"""
Test script to verify SQL Server client sync works correctly
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import ClientAllocation
from main.utils.sql_server_utils import SQLServerConnection
from django.db import transaction

def test_sql_client_sync():
    """Test syncing clients from SQL Server"""

    print("=" * 80)
    print("Testing SQL Server Client Sync")
    print("=" * 80)

    try:
        # Connect to SQL Server
        print("\n[Step 1] Connecting to SQL Server...")
        sql_conn = SQLServerConnection()

        if not sql_conn.connect():
            print("[ERROR] Failed to connect to SQL Server")
            return

        print("[OK] Connected to SQL Server")

        # Fetch all active clients from SQL Server
        print("\n[Step 2] Fetching active clients from SQL Server...")
        cursor = sql_conn.connection.cursor()

        # Query to get all clients with province information
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

        cursor.execute(query)
        sql_clients = cursor.fetchall()

        print(f"[OK] Found {len(sql_clients)} active clients in SQL Server")

        # Show sample of first 3 clients
        print("\n[Sample Data] First 3 clients:")
        for i, row in enumerate(sql_clients[:3], 1):
            print(f"\n  Client {i}:")
            print(f"    ID: {row[0]}")
            print(f"    Name: {row[1]}")
            print(f"    Account Code: {row[2]}")
            print(f"    Province: {row[10]}")

        # Prepare bulk data
        print("\n[Step 3] Preparing bulk records for sync...")
        bulk_records = []
        seen_client_ids = set()

        for row in sql_clients:
            client_id = row[0]
            name = row[1]
            internal_account_code = row[2]
            contact_number = row[3]
            contact_email = row[4]
            contact_number_inspections = row[5]
            contact_email_inspections = row[6]
            site_name = row[7]
            physical_address = row[8]
            is_active = row[9]
            province = row[10]

            # Skip duplicate client IDs
            if client_id in seen_client_ids:
                continue
            seen_client_ids.add(client_id)

            # Use inspection contact info if available, otherwise use general contact info
            phone_number = contact_number_inspections or contact_number
            email = contact_email_inspections or contact_email

            # Determine active status
            active_status = "Active" if is_active else "Inactive"

            # Create ClientAllocation object (not yet saved to DB)
            bulk_records.append(ClientAllocation(
                client_id=client_id,
                facility_type=None,
                group_type=None,
                commodity=None,
                province=province,
                corporate_group=None,
                other=physical_address,
                internal_account_code=internal_account_code,
                allocated=False,
                eclick_name=name,
                representative_email=email,
                phone_number=phone_number,
                duplicates=None,
                active_status=active_status,
                manually_added=False
            ))

        # Close SQL Server connection
        sql_conn.disconnect()
        print(f"[OK] Prepared {len(bulk_records)} records")

        # Get current counts before sync
        print("\n[Step 4] Current database state:")
        current_total = ClientAllocation.objects.count()
        current_manual = ClientAllocation.objects.filter(manually_added=True).count()
        current_synced = ClientAllocation.objects.filter(manually_added=False).count()
        print(f"    Total: {current_total}")
        print(f"    Manual: {current_manual}")
        print(f"    Synced: {current_synced}")

        # Perform sync
        print("\n[Step 5] Syncing to database...")
        with transaction.atomic():
            # Only delete records synced from SQL Server (preserve manually added clients)
            deleted_count = ClientAllocation.objects.filter(manually_added=False).delete()[0]
            print(f"    Deleted {deleted_count} old synced records")

            # Bulk create all records in a single query
            ClientAllocation.objects.bulk_create(bulk_records, batch_size=500)
            print(f"    Created {len(bulk_records)} new records")

        # Get final counts
        print("\n[Step 6] Final database state:")
        final_total = ClientAllocation.objects.count()
        final_manual = ClientAllocation.objects.filter(manually_added=True).count()
        final_synced = ClientAllocation.objects.filter(manually_added=False).count()
        print(f"    Total: {final_total}")
        print(f"    Manual: {final_manual}")
        print(f"    Synced: {final_synced}")

        # Show sample of synced data
        print("\n[Sample Results] First 3 synced clients:")
        sample_clients = ClientAllocation.objects.filter(manually_added=False).order_by('client_id')[:3]
        for client in sample_clients:
            print(f"\n  Client ID {client.client_id}:")
            print(f"    Name: {client.eclick_name}")
            print(f"    Account Code: {client.internal_account_code}")
            print(f"    Province: {client.province}")
            print(f"    Phone: {client.phone_number}")
            print(f"    Email: {client.representative_email}")
            print(f"    Status: {client.active_status}")

        print("\n" + "=" * 80)
        print("[SUCCESS] SQL Server client sync test completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] Failed to sync SQL Server clients: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_sql_client_sync()
