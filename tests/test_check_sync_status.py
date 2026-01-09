import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client as TestClient
from django.contrib.auth import get_user_model
from django.core.cache import cache
import time

def test_check_sync_status():
    """Test the check_sync_status endpoint"""

    print("\nTesting check_sync_status endpoint...")
    print("=" * 80)

    # Create test client
    client = TestClient()

    # Get user and log in
    User = get_user_model()
    user = User.objects.filter(is_superuser=True).first()
    client.force_login(user)

    # Test 1: No progress or result in cache
    print("\n1. Testing with no progress (cache empty)...")
    cache.delete('sync_progress')
    cache.delete('sync_result')

    response = client.get('/check-sync-status/')
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.get('Content-Type')}")

    if response.status_code == 200:
        import json
        data = json.loads(response.content)
        print(f"   Response: {data}")

    # Test 2: With progress in cache
    print("\n2. Testing with progress in cache...")
    cache.set('sync_progress', {
        'status': 'running',
        'current': 250,
        'total': 1000,
        'percent': 25,
        'message': 'Processing inspections...'
    })

    response = client.get('/check-sync-status/')
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        import json
        data = json.loads(response.content)
        print(f"   Response: {data}")

    # Test 3: With result in cache (completed)
    print("\n3. Testing with completed result in cache...")
    cache.set('sync_result', {
        'success': True,
        'message': 'Sync completed successfully!',
        'created_count': 1000,
        'total_processed': 1000
    })
    cache.set('sync_progress', {
        'status': 'completed',
        'current': 1000,
        'total': 1000,
        'percent': 100
    })

    response = client.get('/check-sync-status/')
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        import json
        data = json.loads(response.content)
        print(f"   Response: {data}")

    # Test 4: Check if URL exists
    print("\n4. Checking URL pattern...")
    from django.urls import resolve, reverse
    try:
        url = reverse('check_sync_status')
        print(f"   URL: {url}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 80)

if __name__ == '__main__':
    test_check_sync_status()
