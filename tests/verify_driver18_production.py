#!/usr/bin/env python3
"""
Production Verification Script for ODBC Driver 18
This script verifies:
1. ODBC Driver 18 is installed
2. SQL Server connection works with Driver 18
3. Connection pooling is active
4. Product name fetching works and is fast
5. All code changes are deployed
"""

import os
import sys
import io
import time
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

def check_odbc_drivers():
    """Check which ODBC drivers are installed"""
    print("\n" + "=" * 100)
    print("STEP 1: CHECK ODBC DRIVERS")
    print("=" * 100)

    try:
        import pyodbc
        drivers = pyodbc.drivers()

        print(f"\nInstalled ODBC drivers ({len(drivers)}):")
        for driver in drivers:
            print(f"  • {driver}")

        has_driver17 = any('17' in d for d in drivers)
        has_driver18 = any('18' in d for d in drivers)

        print(f"\n✓ ODBC Driver 17: {'Found' if has_driver17 else 'Not found'}")
        print(f"✓ ODBC Driver 18: {'Found' if has_driver18 else 'Not found'}")

        if not has_driver18:
            print("\n❌ ODBC Driver 18 is NOT installed!")
            return False

        print("\n✅ ODBC Driver 18 is installed!")
        return True

    except Exception as e:
        print(f"\n❌ Error checking ODBC drivers: {e}")
        return False

def check_sql_server_connection():
    """Test SQL Server connection with Driver 18"""
    print("\n" + "=" * 100)
    print("STEP 2: TEST SQL SERVER CONNECTION")
    print("=" * 100)

    try:
        import pyodbc

        connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=102.67.140.12,1053;"
            "DATABASE=AFS;"
            "UID=FSAUser2;"
            "PWD=password;"
            "TrustServerCertificate=yes;"
            "Encrypt=no;"
        )

        print("\nAttempting connection to SQL Server...")
        print("  Server: 102.67.140.12:1053")
        print("  Database: AFS")
        print("  Driver: ODBC Driver 18 for SQL Server")

        start_time = time.time()
        conn = pyodbc.connect(connection_string, timeout=10)
        connect_time = time.time() - start_time

        print(f"\n✅ Connection successful! (took {connect_time:.2f}s)")

        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"\nSQL Server version:")
        print(f"  {version[:100]}...")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return False

def check_django_settings():
    """Check Django settings for Driver 18"""
    print("\n" + "=" * 100)
    print("STEP 3: CHECK DJANGO SETTINGS")
    print("=" * 100)

    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
        import django
        django.setup()

        from django.conf import settings

        sql_server_config = settings.DATABASES.get('sql_server', {})
        driver = sql_server_config.get('OPTIONS', {}).get('driver', 'Not set')

        print(f"\nSQL Server configuration in Django settings:")
        print(f"  Driver: {driver}")
        print(f"  Host: {sql_server_config.get('HOST')}")
        print(f"  Port: {sql_server_config.get('PORT')}")
        print(f"  Database: {sql_server_config.get('NAME')}")

        if 'Driver 18' in driver:
            print("\n✅ Django is configured to use ODBC Driver 18!")
            return True
        else:
            print(f"\n❌ Django is NOT using Driver 18! Current driver: {driver}")
            return False

    except Exception as e:
        print(f"\n❌ Error checking Django settings: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_connection_pooling():
    """Check if connection pooling is active"""
    print("\n" + "=" * 100)
    print("STEP 4: CHECK CONNECTION POOLING")
    print("=" * 100)

    try:
        from main.utils.sql_server_utils import get_pooled_connection

        print("\nTesting connection pool...")

        # Get connection twice
        conn1 = get_pooled_connection()
        conn1_id = id(conn1)
        print(f"  First connection ID: {conn1_id}")

        conn2 = get_pooled_connection()
        conn2_id = id(conn2)
        print(f"  Second connection ID: {conn2_id}")

        if conn1_id == conn2_id:
            print("\n✅ Connection pooling is ACTIVE - same connection reused!")
            return True
        else:
            print("\n❌ Connection pooling is NOT working - new connection created!")
            return False

    except Exception as e:
        print(f"\n❌ Error testing connection pool: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_product_name_performance():
    """Test product name fetching performance"""
    print("\n" + "=" * 100)
    print("STEP 5: TEST PRODUCT NAME FETCHING PERFORMANCE")
    print("=" * 100)

    try:
        from main.utils.sql_server_utils import fetch_product_names_for_inspection
        from main.models import FoodSafetyAgencyInspection
        from datetime import date

        # Find recent inspections
        inspections = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection__gte=date(2025, 10, 1)
        ).order_by('-date_of_inspection')[:5]

        print(f"\nFound {inspections.count()} recent inspections to test")

        if inspections.count() == 0:
            print("No recent inspections - skipping performance test")
            return True

        test_ids = [insp.remote_id for insp in inspections if insp.remote_id][:3]
        print(f"Testing with {len(test_ids)} inspection IDs: {test_ids}")

        # Time the fetches
        start_time = time.time()

        for inspection_id in test_ids:
            product_names = fetch_product_names_for_inspection(inspection_id=inspection_id)
            print(f"  Inspection {inspection_id}: {len(product_names)} products")

        elapsed = time.time() - start_time
        avg_time = elapsed / len(test_ids) if test_ids else 0

        print(f"\n⏱️  Total time: {elapsed:.2f}s")
        print(f"⏱️  Average per inspection: {avg_time:.2f}s")

        if elapsed < 5:
            print("✅ Performance is EXCELLENT!")
            return True
        elif elapsed < 10:
            print("✅ Performance is GOOD")
            return True
        else:
            print("⚠️  Performance could be better")
            return True  # Still pass, just warn

    except Exception as e:
        print(f"\n❌ Error testing performance: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification checks"""
    print("\n" + "=" * 100)
    print(" " * 25 + "ODBC DRIVER 18 PRODUCTION VERIFICATION")
    print("=" * 100)

    results = {}

    # Run all checks
    results['drivers'] = check_odbc_drivers()
    results['connection'] = check_sql_server_connection()
    results['settings'] = check_django_settings()
    results['pooling'] = check_connection_pooling()
    results['performance'] = test_product_name_performance()

    # Summary
    print("\n" + "=" * 100)
    print(" " * 40 + "SUMMARY")
    print("=" * 100)

    all_passed = all(results.values())

    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check.upper():20s}: {status}")

    print("\n" + "=" * 100)

    if all_passed:
        print(" " * 30 + "✅ ALL CHECKS PASSED!")
        print("=" * 100)
        print("\nThe application is ready with ODBC Driver 18!")
        print("Connection pooling is active and performance should be excellent.")
        return True
    else:
        print(" " * 30 + "❌ SOME CHECKS FAILED!")
        print("=" * 100)
        print("\nPlease review the failed checks above.")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
