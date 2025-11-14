"""
Debug is_sent - Check what the shipment_list view actually sees
"""

import os
import sys
import io
import django
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# Import after Django setup
from main.models import FoodSafetyAgencyInspection
from datetime import date

def debug_is_sent():
    """Check what the view sees for is_sent"""

    print("="*100)
    print(" " * 35 + "DEBUG IS_SENT")
    print("="*100)

    client_name = "Hume International"
    inspection_date = date(2025, 10, 17)

    # Simulate what the view does - fresh query WITHOUT select_related
    print("\n[TEST 1] Simple query (what user sees in browser)...")
    inspections_simple = FoodSafetyAgencyInspection.objects.filter(
        client_name=client_name,
        date_of_inspection=inspection_date
    )

    print(f"Found {inspections_simple.count()} inspections")
    for insp in inspections_simple:
        print(f"  ID: {insp.id}, is_sent: {insp.is_sent}, sent_date: {insp.sent_date}")

    group_is_sent = any(inspection.is_sent for inspection in inspections_simple)
    print(f"\ngroup_is_sent (simple): {group_is_sent}")

    # Simulate what the view does - with select_related
    print("\n[TEST 2] Query with select_related (what view does)...")
    inspections_view = FoodSafetyAgencyInspection.objects.select_related('rfi_uploaded_by', 'invoice_uploaded_by', 'sent_by').filter(
        client_name=client_name,
        date_of_inspection=inspection_date
    )

    print(f"Found {inspections_view.count()} inspections")
    for insp in inspections_view:
        print(f"  ID: {insp.id}, is_sent: {insp.is_sent}, sent_date: {insp.sent_date}, sent_by: {insp.sent_by}")

    group_is_sent_view = any(inspection.is_sent for inspection in inspections_view)
    print(f"\ngroup_is_sent (view style): {group_is_sent_view}")

    # Force a database refresh
    print("\n[TEST 3] Force refresh from database...")
    from django.db import connection
    connection.close()

    inspections_fresh = FoodSafetyAgencyInspection.objects.filter(
        client_name=client_name,
        date_of_inspection=inspection_date
    )

    print(f"Found {inspections_fresh.count()} inspections")
    for insp in inspections_fresh:
        print(f"  ID: {insp.id}, is_sent: {insp.is_sent}, sent_date: {insp.sent_date}")

    group_is_sent_fresh = any(inspection.is_sent for inspection in inspections_fresh)
    print(f"\ngroup_is_sent (fresh): {group_is_sent_fresh}")

    # Check raw SQL
    print("\n[TEST 4] Raw SQL query...")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, client_name, is_sent, sent_date
        FROM main_foodsafetyagencyinspection
        WHERE client_name = %s AND date_of_inspection = %s
    """, [client_name, inspection_date])

    rows = cursor.fetchall()
    print(f"Found {len(rows)} rows")
    for row in rows:
        print(f"  ID: {row[0]}, client: {row[1]}, is_sent: {row[2]}, sent_date: {row[3]}")

    print("\n" + "="*100)
    print("DIAGNOSIS")
    print("="*100)

    if group_is_sent_fresh:
        print("\n✅ Database shows is_sent=True")
        print("   The view SHOULD show 'Sent' status")
        print("\n   If browser shows 'Not Sent', the issue is:")
        print("   - Template caching")
        print("   - Browser caching")
        print("   - View caching")
    else:
        print("\n❌ Database shows is_sent=False")
        print("   This is wrong! Run mark_as_sent.py again")

    return group_is_sent_fresh


if __name__ == '__main__':
    print("\n🔍 Starting is_sent debug...\n")

    result = debug_is_sent()

    sys.exit(0 if result else 1)
