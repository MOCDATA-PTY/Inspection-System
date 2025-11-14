"""
Test connection pooling performance with ODBC Driver 18
This test will:
1. Test fetching product names with connection pooling
2. Measure performance (should be fast)
3. Verify the connection pool is working correctly
"""

import os
import sys
import io
import django
import time
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
from main.utils.sql_server_utils import fetch_product_names_for_inspection, get_pooled_connection
from main.models import FoodSafetyAgencyInspection
from datetime import date

def test_connection_pool():
    """Test that connection pool is working"""
    print("=" * 100)
    print(" " * 30 + "CONNECTION POOLING TEST")
    print("=" * 100)

    # Test 1: Get pooled connection multiple times - should return same connection
    print("\nTest 1: Connection Pool Reuse")
    print("-" * 100)

    conn1 = get_pooled_connection()
    conn1_id = id(conn1)
    print(f"First connection ID: {conn1_id}")

    conn2 = get_pooled_connection()
    conn2_id = id(conn2)
    print(f"Second connection ID: {conn2_id}")

    if conn1_id == conn2_id:
        print("✅ Connection pool is working - same connection reused!")
    else:
        print("❌ Connection pool NOT working - new connection created!")
        return False

    # Test 2: Test product name fetching performance
    print("\n\nTest 2: Product Name Fetching Performance")
    print("-" * 100)

    # Find a recent inspection with multiple commodities
    inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=date(2025, 10, 1)
    ).order_by('-date_of_inspection')[:10]

    print(f"\nFound {inspections.count()} recent inspections to test")

    if inspections.count() == 0:
        print("No recent inspections found - using test inspection ID")
        test_ids = [1, 2, 3]
    else:
        test_ids = [insp.remote_id for insp in inspections if insp.remote_id][:5]

    print(f"Testing with {len(test_ids)} inspection IDs: {test_ids}")

    # Time the product name fetches
    start_time = time.time()

    for inspection_id in test_ids:
        product_names = fetch_product_names_for_inspection(inspection_id=inspection_id)
        print(f"  Inspection {inspection_id}: Found {len(product_names)} products - {product_names[:3]}...")

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"\n{'='*100}")
    print(f"⏱️  Total time for {len(test_ids)} inspections: {elapsed:.2f} seconds")
    print(f"⏱️  Average time per inspection: {elapsed/len(test_ids):.2f} seconds")

    if elapsed < 5:
        print("✅ Performance is EXCELLENT!")
    elif elapsed < 10:
        print("✅ Performance is GOOD")
    elif elapsed < 30:
        print("⚠️  Performance is ACCEPTABLE but could be better")
    else:
        print("❌ Performance is POOR - investigate further")
        return False

    # Test 3: Verify connection is still alive after multiple queries
    print("\n\nTest 3: Connection Health After Multiple Queries")
    print("-" * 100)

    try:
        conn = get_pooled_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()

        if result[0] == 1:
            print("✅ Connection is still healthy after multiple queries!")
        else:
            print("❌ Connection test failed!")
            return False
    except Exception as e:
        print(f"❌ Connection health check failed: {e}")
        return False

    print("\n" + "=" * 100)
    print(" " * 35 + "✅ ALL TESTS PASSED!")
    print("=" * 100)
    print("\nConnection pooling is working correctly with ODBC Driver 18!")
    print("The application should now have fast performance like it did with Driver 17.")

    return True

if __name__ == '__main__':
    try:
        success = test_connection_pool()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
