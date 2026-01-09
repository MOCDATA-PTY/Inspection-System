import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from main.views.core_views import refresh_clients

def test_refresh_clients_endpoint():
    """Test the refresh_clients endpoint directly"""

    print("Testing refresh_clients endpoint...")
    print()

    # Create a fake request
    factory = RequestFactory()
    request = factory.post('/refresh_clients/')

    # Add session support
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()

    # Add a fake user
    User = get_user_model()
    try:
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            print("ERROR: No superuser found in database")
            return
        request.user = user
    except Exception as e:
        print(f"ERROR getting user: {e}")
        return

    # Add headers to simulate AJAX request
    request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

    print(f"Calling refresh_clients as user: {user.username}")
    print()

    try:
        response = refresh_clients(request)

        print("Response received!")
        print(f"Status code: {response.status_code}")
        print()

        if hasattr(response, 'content'):
            import json
            try:
                data = json.loads(response.content)
                print("Response JSON:")
                print(json.dumps(data, indent=2))

                if data.get('success'):
                    print("\n✓ SUCCESS! Client sync worked!")
                else:
                    print(f"\n✗ FAILED: {data.get('error', 'Unknown error')}")
            except:
                print("Response content (not JSON):")
                print(response.content.decode('utf-8')[:500])

    except Exception as e:
        print(f"EXCEPTION occurred: {e}")
        print()
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_refresh_clients_endpoint()
