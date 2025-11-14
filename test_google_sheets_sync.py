#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Google Sheets client name sync functionality
Diagnose why client names aren't updating
"""
import os
import sys
import django

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, Client

print("\n" + "="*80)
print("GOOGLE SHEETS CLIENT NAME SYNC DIAGNOSTIC")
print("="*80)
print("\nChecking why client name didn't update for account code: RE-IND-RAW-NA-0222\n")

def check_google_sheets_client_table():
    """Check if Google Sheets client exists in Django Client table"""
    print("="*80)
    print("STEP 1: Checking Google Sheets (Django Client Table)")
    print("="*80)

    account_code = "RE-IND-RAW-NA-0222"

    print(f"\nSearching for account code: {account_code}")
    print("-"*80)

    # Try exact match
    clients = Client.objects.filter(internal_account_code=account_code)

    if clients.exists():
        print(f"✓ Found {clients.count()} client(s) with account code '{account_code}':")
        for client in clients:
            print(f"\n  Client ID: {client.client_id}")
            print(f"  Client Name: {client.name}")
            print(f"  Account Code: {client.internal_account_code}")
            print(f"  Email: {client.email or 'None'}")
            print(f"  Created: {client.created_at}")
            print(f"  Updated: {client.updated_at}")
    else:
        print(f"✗ No client found with account code '{account_code}'")

        # Try case-insensitive search
        print(f"\n  Trying case-insensitive search...")
        clients_icase = Client.objects.filter(internal_account_code__iexact=account_code)

        if clients_icase.exists():
            print(f"  ✓ Found {clients_icase.count()} client(s) with case-insensitive match:")
            for client in clients_icase:
                print(f"    Account Code (actual): '{client.internal_account_code}'")
                print(f"    Account Code (search): '{account_code}'")
                print(f"    Match: {client.internal_account_code == account_code}")
        else:
            print(f"  ✗ No clients found even with case-insensitive search")

        # Show all clients with similar codes
        print(f"\n  Searching for similar account codes...")
        similar_clients = Client.objects.filter(internal_account_code__icontains='RE-IND')[:10]

        if similar_clients.exists():
            print(f"  Found {similar_clients.count()} clients with 'RE-IND' in account code:")
            for client in similar_clients:
                print(f"    {client.internal_account_code:30s} → {client.name}")

    return clients.exists()

def check_inspections_with_account_code():
    """Check inspections with the specific account code"""
    print("\n" + "="*80)
    print("STEP 2: Checking Inspections with Account Code")
    print("="*80)

    account_code = "RE-IND-RAW-NA-0222"

    print(f"\nSearching for inspections with account code: {account_code}")
    print("-"*80)

    # Try exact match
    inspections = FoodSafetyAgencyInspection.objects.filter(
        internal_account_code=account_code
    )

    if inspections.exists():
        print(f"✓ Found {inspections.count()} inspection(s) with account code '{account_code}':")

        for idx, insp in enumerate(inspections[:5], 1):
            print(f"\n  Inspection #{idx}:")
            print(f"    ID: {insp.id}")
            print(f"    Client Name: {insp.client_name}")
            print(f"    Account Code: {insp.internal_account_code}")
            print(f"    Date: {insp.date_of_inspection}")
            print(f"    Commodity: {insp.commodity}")
            print(f"    Updated: {insp.updated_at}")

        if inspections.count() > 5:
            print(f"\n  ... and {inspections.count() - 5} more")
    else:
        print(f"✗ No inspections found with account code '{account_code}'")

        # Try case-insensitive
        inspections_icase = FoodSafetyAgencyInspection.objects.filter(
            internal_account_code__iexact=account_code
        )

        if inspections_icase.exists():
            print(f"  ✓ Found {inspections_icase.count()} inspection(s) with case-insensitive match")

        # Check if field is populated at all
        with_code = FoodSafetyAgencyInspection.objects.exclude(
            internal_account_code__isnull=True
        ).exclude(internal_account_code='').count()

        total = FoodSafetyAgencyInspection.objects.count()

        print(f"\n  Database statistics:")
        print(f"    Total inspections: {total}")
        print(f"    With account code: {with_code} ({(with_code/total*100) if total > 0 else 0:.1f}%)")
        print(f"    Without account code: {total - with_code} ({((total-with_code)/total*100) if total > 0 else 0:.1f}%)")

    return inspections.exists()

def check_todays_inspections():
    """Check today's inspections"""
    print("\n" + "="*80)
    print("STEP 3: Checking Today's Inspections")
    print("="*80)

    from datetime import date
    today = date.today()

    print(f"\nSearching for inspections from today: {today}")
    print("-"*80)

    todays_inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection=today
    )

    if todays_inspections.exists():
        print(f"✓ Found {todays_inspections.count()} inspection(s) from today:")

        for idx, insp in enumerate(todays_inspections, 1):
            print(f"\n  Inspection #{idx}:")
            print(f"    ID: {insp.id}")
            print(f"    Client Name: {insp.client_name}")
            print(f"    Account Code: {insp.internal_account_code or 'NONE!'}")
            print(f"    Date: {insp.date_of_inspection}")
            print(f"    Inspector: {insp.inspector_name}")
            print(f"    Updated: {insp.updated_at}")

            # Check if account code matches
            if insp.internal_account_code == "RE-IND-RAW-NA-0222":
                print(f"    ✓ This is the inspection you're looking for!")

                # Check if Google Sheets has a match
                google_client = Client.objects.filter(
                    internal_account_code=insp.internal_account_code
                ).first()

                if google_client:
                    print(f"    ✓ Google Sheets match found:")
                    print(f"      Google Sheets Name: {google_client.name}")
                    print(f"      Inspection Name: {insp.client_name}")
                    print(f"      Names Match: {google_client.name == insp.client_name}")

                    if google_client.name != insp.client_name:
                        print(f"    ⚠️  MISMATCH! Inspection needs to be resynced!")
                else:
                    print(f"    ✗ No Google Sheets match found!")
    else:
        print(f"✗ No inspections found from today")

    return todays_inspections.exists()

def test_matching_logic():
    """Test the matching logic manually"""
    print("\n" + "="*80)
    print("STEP 4: Testing Matching Logic")
    print("="*80)

    account_code = "RE-IND-RAW-NA-0222"

    print(f"\nSimulating sync matching for account code: {account_code}")
    print("-"*80)

    # This is exactly what the sync code does
    google_client = Client.objects.filter(
        internal_account_code=account_code
    ).first()

    if google_client:
        print(f"✓ Match successful!")
        print(f"  Google Sheets Client Name: {google_client.name}")
        print(f"  This name would be used for the inspection")
    else:
        print(f"✗ No match found!")
        print(f"  Would fall back to SQL Server client name")

        # Debug why no match
        print(f"\n  Debugging:")
        all_codes = Client.objects.values_list('internal_account_code', flat=True)
        all_codes_list = list(all_codes)[:20]
        print(f"  First 20 account codes in database:")
        for code in all_codes_list:
            print(f"    '{code}'")

def show_sync_recommendations():
    """Show recommendations for fixing the sync"""
    print("\n" + "="*80)
    print("SYNC RECOMMENDATIONS")
    print("="*80)

    print("""
Based on the diagnostic results above, here's what to do:

1. CHECK GOOGLE SHEETS SYNC:
   - Did you run Google Sheets sync FIRST?
   - Check if Client table has the updated name
   - Look at STEP 1 results above

2. CHECK SQL SERVER SYNC:
   - Did you run SQL Server sync AFTER Google Sheets?
   - Check if inspections have account codes populated
   - Look at STEP 2 and STEP 3 results above

3. CORRECT SYNC ORDER:
   a. Sync Google Sheets FIRST
      → This updates the Client table with your new name

   b. Sync SQL Server SECOND
      → This matches inspections with Client table and updates names

4. VERIFY THE FIX:
   - After syncing, check STEP 3 output
   - "Names Match" should be True
   - Inspection name should equal Google Sheets name

5. IF STILL NOT WORKING:
   - Check if account codes match EXACTLY
   - Check for extra spaces or different cases
   - Verify Google Sheets has the data in correct columns:
     • Column H: Account Code
     • Column J: Client Name
    """)

def main():
    """Run all diagnostic tests"""
    try:
        print("\n" + "="*80)
        print("RUNNING DIAGNOSTICS")
        print("="*80)

        google_sheets_ok = check_google_sheets_client_table()
        inspections_ok = check_inspections_with_account_code()
        todays_ok = check_todays_inspections()
        test_matching_logic()

        # Summary
        print("\n" + "="*80)
        print("DIAGNOSTIC SUMMARY")
        print("="*80)

        print(f"\n✓ Google Sheets Client Found: {google_sheets_ok}")
        print(f"✓ Inspections with Account Code Found: {inspections_ok}")
        print(f"✓ Today's Inspections Found: {todays_ok}")

        if not google_sheets_ok:
            print("\n⚠️  PROBLEM: Google Sheets client not found!")
            print("   ACTION: Run Google Sheets sync to populate Client table")

        if not inspections_ok:
            print("\n⚠️  PROBLEM: No inspections with account code!")
            print("   ACTION: Run SQL Server sync to populate account codes")

        if google_sheets_ok and inspections_ok:
            print("\n✓ Both Google Sheets and Inspections have data")
            print("  Now checking if names match...")

        show_sync_recommendations()

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
