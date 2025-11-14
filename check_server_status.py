import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

print("\n" + "="*60)
print("SERVER STATUS DIAGNOSTIC")
print("="*60 + "\n")

# 1. Check PostgreSQL
print("1. PostgreSQL Database")
print("-" * 40)
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    print("[OK] Status: ONLINE")
    print(f"  Result: {result}")
except Exception as e:
    print("[FAIL] Status: OFFLINE")
    print(f"  Error: {e}")

# 2. Check SQL Server
print("\n2. SQL Server Database")
print("-" * 40)
try:
    import pyodbc
    from main.views.data_views import SQLSERVER_CONNECTION_STRING

    print(f"  Connection String: {SQLSERVER_CONNECTION_STRING[:100]}...")
    print(f"  Attempting connection with 5 second timeout...")

    conn = pyodbc.connect(SQLSERVER_CONNECTION_STRING, timeout=5)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    print("[OK] Status: ONLINE")
    print(f"  Result: {result}")
except ImportError as e:
    print("[FAIL] Status: ERROR - pyodbc not installed")
    print(f"  Error: {e}")
except Exception as e:
    print("[FAIL] Status: OFFLINE")
    print(f"  Error: {e}")
    print(f"  Error Type: {type(e).__name__}")

# 3. Check Google Sheets
print("\n3. Google Sheets API")
print("-" * 40)
try:
    from main.services.google_sheets_service import GoogleSheetsService

    service = GoogleSheetsService()
    is_connected, message = service.check_connection_status()

    if is_connected:
        print("[OK] Status: CONNECTED")
        print(f"  Message: {message}")
    else:
        print("[FAIL] Status: DISCONNECTED")
        print(f"  Message: {message}")
except Exception as e:
    print("[FAIL] Status: ERROR")
    print(f"  Error: {e}")
    print(f"  Error Type: {type(e).__name__}")

# 4. Check last sync
print("\n4. Last Sync Status")
print("-" * 40)
try:
    from main.models import FoodSafetyAgencyInspection
    from django.utils import timezone

    latest_inspection = FoodSafetyAgencyInspection.objects.order_by('-created_at').first()
    if latest_inspection:
        now = timezone.now()
        time_diff = now - latest_inspection.created_at
        hours_ago = time_diff.total_seconds() / 3600

        print(f"  Last Sync: {int(hours_ago)} hours ago")
        print(f"  Last Record: {latest_inspection.created_at}")
    else:
        print("  No inspection records found")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*60)
print("END OF DIAGNOSTIC")
print("="*60 + "\n")
