import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import RequestFactory, Client as TestClient
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from main.views.core_views import refresh_clients, refresh_inspections
from main.middleware import SessionTimeoutMiddleware
from django.utils import timezone

def test_multi_step_sync():
    """Test the multi-step sync to see if session persists"""

    print("\nTesting multi-step sync (clients -> inspections)...")
    print("=" * 80)

    # Create a test client with session support
    client = TestClient()

    # Get a superuser
    User = get_user_model()
    user = User.objects.filter(is_superuser=True).first()

    if not user:
        print("ERROR: No superuser found")
        return

    # Log in
    print(f"\n1. Logging in as {user.username}...")
    client.force_login(user)

    # Check session before client sync
    session = client.session
    print(f"   Session key: {session.session_key}")
    print(f"   Last activity: {session.get('last_activity', 'NOT SET')}")

    # Step 1: Call refresh_clients
    print(f"\n2. Calling refresh_clients endpoint...")
    print(f"   Time before: {timezone.now().isoformat()}")

    response1 = client.post(
        '/refresh-clients/',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )

    print(f"   Response status: {response1.status_code}")
    print(f"   Response content-type: {response1.get('Content-Type', 'NOT SET')}")

    if response1.status_code == 200:
        try:
            import json
            data = json.loads(response1.content)
            print(f"   Response: {data}")
        except:
            print(f"   Response (first 200 chars): {response1.content.decode('utf-8')[:200]}")

    # Check session after client sync
    print(f"\n3. Checking session after client sync...")
    session = client.session
    print(f"   Session key: {session.session_key}")
    print(f"   Last activity: {session.get('last_activity', 'NOT SET')}")
    print(f"   Session age: {session.get_session_cookie_age()} seconds")
    print(f"   Time now: {timezone.now().isoformat()}")

    # Check if user is still authenticated
    print(f"\n4. Checking authentication status...")
    print(f"   User authenticated: {client.session.get('_auth_user_id') is not None}")

    # Step 2: Call refresh_inspections
    print(f"\n5. Calling refresh_inspections endpoint...")
    print(f"   Time before: {timezone.now().isoformat()}")

    response2 = client.post(
        '/refresh-inspections/',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )

    print(f"   Response status: {response2.status_code}")
    print(f"   Response content-type: {response2.get('Content-Type', 'NOT SET')}")

    if response2.status_code == 200:
        try:
            import json
            data = json.loads(response2.content)
            print(f"   Response: {data}")
        except:
            print(f"   Response (first 500 chars): {response2.content.decode('utf-8')[:500]}")

    # Check session after inspection sync
    print(f"\n6. Checking session after inspection sync...")
    session = client.session
    print(f"   Session key: {session.session_key}")
    print(f"   Last activity: {session.get('last_activity', 'NOT SET')}")
    print(f"   Time now: {timezone.now().isoformat()}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print(f"  Client sync: {response1.status_code} - {'JSON' if 'application/json' in response1.get('Content-Type', '') else 'HTML'}")
    print(f"  Inspection sync: {response2.status_code} - {'JSON' if 'application/json' in response2.get('Content-Type', '') else 'HTML'}")

    if response2.status_code == 200 and 'text/html' in response2.get('Content-Type', ''):
        print("\n  [!] ISSUE: Inspection sync returned HTML instead of JSON!")
        print("  This indicates the session expired or user was logged out.")
    else:
        print("\n  [OK] SUCCESS: Both endpoints returned appropriate responses")

if __name__ == '__main__':
    test_multi_step_sync()
