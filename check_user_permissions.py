#!/usr/bin/env python3
"""
Check user permissions and view filtering
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User
from main.views.core_views import shipment_list
from django.test import RequestFactory

def check_user_permissions():
    """Check user permissions and view filtering"""
    print("🔍 Checking user permissions and view filtering...")
    
    try:
        # Get the test user
        user = User.objects.get(username='testuser')
        print(f"👤 User: {user.username}")
        print(f"    Is active: {user.is_active}")
        print(f"    Is staff: {user.is_staff}")
        print(f"    Is superuser: {user.is_superuser}")
        
        # Check if user has role attribute
        if hasattr(user, 'role'):
            print(f"    Role: {user.role}")
        else:
            print("    Role: No role attribute")
            
        # Test the view directly
        factory = RequestFactory()
        request = factory.get('/inspections/')
        request.user = user
        
        # Mock the clear_messages function to avoid the error
        import main.views.utils
        original_clear_messages = main.views.utils.clear_messages
        def mock_clear_messages(request):
            pass
        main.views.utils.clear_messages = mock_clear_messages
        
        try:
            response = shipment_list(request)
            print(f"✅ View returned status: {response.status_code}")
            
            if hasattr(response, 'context_data'):
                shipments = response.context_data.get('shipments', [])
                print(f"📊 Shipments in context: {len(shipments)}")
                
                if len(shipments) > 0:
                    print("✅ Shipments data found!")
                    first_shipment = shipments[0]
                    print(f"    First shipment: {first_shipment.get('client_name', 'No client_name')}")
                    print(f"    Products: {len(first_shipment.get('products', []))}")
                else:
                    print("❌ No shipments data found")
            else:
                print("❌ No context_data in response")
                
        finally:
            # Restore original function
            main.views.utils.clear_messages = original_clear_messages
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_user_permissions()
