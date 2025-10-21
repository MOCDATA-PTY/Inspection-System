"""
Production Server Diagnostic Script
Run this on the production server at 82.25.97.159 to diagnose connection issues
"""
import os
import django
import socket

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

print("\n" + "="*70)
print("PRODUCTION SERVER DIAGNOSTIC - 82.25.97.159")
print("="*70 + "\n")

# 1. Check PostgreSQL
print("1. PostgreSQL Database (Local)")
print("-" * 70)
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

# 2. Test network connectivity to SQL Server
print("\n2. Network Connectivity to SQL Server (102.67.140.12:1053)")
print("-" * 70)
try:
    sql_host = "102.67.140.12"
    sql_port = 1053
    timeout = 5

    print(f"  Testing connection to {sql_host}:{sql_port} with {timeout}s timeout...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((sql_host, sql_port))
    sock.close()

    if result == 0:
        print(f"[OK] Network connection successful to {sql_host}:{sql_port}")
    else:
        print(f"[FAIL] Cannot connect to {sql_host}:{sql_port}")
        print(f"  Error code: {result}")
        print("  Possible causes:")
        print("    - Firewall blocking outbound connections")
        print("    - SQL Server is down")
        print("    - Network routing issue")
except Exception as e:
    print(f"[FAIL] Network test failed")
    print(f"  Error: {e}")

# 3. Check SQL Server with pyodbc
print("\n3. SQL Server Database Connection")
print("-" * 70)
try:
    import pyodbc
    print("[OK] pyodbc module is installed")

    # Check available ODBC drivers
    drivers = [driver for driver in pyodbc.drivers()]
    print(f"  Available ODBC drivers: {', '.join(drivers)}")

    if 'ODBC Driver 17 for SQL Server' not in drivers:
        print("[WARN] ODBC Driver 17 for SQL Server not found!")
        print("  You may need to install it on the production server")
        print("  Available drivers:", drivers)

    from main.views.data_views import SQLSERVER_CONNECTION_STRING

    print(f"\n  Attempting SQL Server connection...")
    print(f"  Server: 102.67.140.12,1053")
    print(f"  Database: AFS")
    print(f"  Timeout: 5 seconds")

    conn = pyodbc.connect(SQLSERVER_CONNECTION_STRING, timeout=5)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    print("[OK] SQL Server connection successful")
    print(f"  Result: {result}")

except ImportError as e:
    print("[FAIL] pyodbc module not installed")
    print(f"  Error: {e}")
    print("  Solution: Install pyodbc on production server")
    print("    pip install pyodbc")

except Exception as e:
    print("[FAIL] SQL Server connection failed")
    print(f"  Error: {e}")
    print(f"  Error Type: {type(e).__name__}")

# 4. Check Google Sheets credentials
print("\n4. Google Sheets API")
print("-" * 70)
try:
    from main.services.google_sheets_service import GoogleSheetsService

    service = GoogleSheetsService()

    # Check if token file exists
    if os.path.exists(service.token_path):
        print(f"[OK] Token file found: {service.token_path}")
    else:
        print(f"[FAIL] Token file not found: {service.token_path}")
        print("  Solution: Copy token.pickle from local to production server")

    # Check if credentials file exists
    if os.path.exists(service.credentials_path):
        print(f"[OK] Credentials file found: {service.credentials_path}")
    else:
        print(f"[FAIL] Credentials file not found: {service.credentials_path}")
        print("  Solution: Copy credentials.json from local to production server")

    # Try to connect
    print(f"\n  Attempting Google Sheets connection...")
    is_connected, message = service.check_connection_status()

    if is_connected:
        print("[OK] Google Sheets connection successful")
        print(f"  Message: {message}")
    else:
        print("[FAIL] Google Sheets connection failed")
        print(f"  Message: {message}")

except Exception as e:
    print("[FAIL] Google Sheets check failed")
    print(f"  Error: {e}")
    print(f"  Error Type: {type(e).__name__}")

# 5. Check cache system
print("\n5. Cache System")
print("-" * 70)
try:
    from django.core.cache import cache
    from django.conf import settings

    cache_backend = settings.CACHES.get('default', {}).get('BACKEND', 'Unknown')
    print(f"  Cache backend: {cache_backend}")

    # Test cache
    test_key = 'diagnostic_test_key'
    test_value = 'diagnostic_test_value'

    cache.set(test_key, test_value, 10)
    retrieved_value = cache.get(test_key)

    if retrieved_value == test_value:
        print("[OK] Cache is working")
        cache.delete(test_key)
    else:
        print("[WARN] Cache test failed")

except Exception as e:
    print(f"[FAIL] Cache check failed: {e}")

# 6. Check environment info
print("\n6. Environment Information")
print("-" * 70)
print(f"  Python version: {os.sys.version}")
print(f"  Django settings: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')}")
print(f"  Current working directory: {os.getcwd()}")

# 7. Recommendations
print("\n" + "="*70)
print("RECOMMENDATIONS")
print("="*70)
print("""
If SQL Server shows offline on production:
1. Check if production server firewall allows outbound connections to 102.67.140.12:1053
2. Verify ODBC Driver 17 is installed on production server
3. Check if SQL Server credentials are correct
4. Clear cache on production: python clear_status_cache.py

If Google Sheets shows disconnected:
1. Copy credentials.json from local to production server
2. Copy token.pickle from local to production server
3. Ensure files are in the correct location
4. Check file permissions

After making changes:
1. Clear the cache: python clear_status_cache.py
2. Refresh dashboard with ?refresh_status=true
""")

print("="*70 + "\n")
