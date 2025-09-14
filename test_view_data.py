#!/usr/bin/env python3
"""
Test script to check view data directly
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.views.core_views import shipment_list
from django.test import RequestFactory
from django.contrib.auth.models import User

def test_view_data():
    """Test the shipment_list view directly"""
    print("🔍 Testing shipment_list view directly...")
    
    try:
        # Create a test request
        factory = RequestFactory()
        request = factory.get('/inspections/')
        
        # Create a test user (or get existing one)
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                print("❌ No superuser found")
                return False
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return False
        
        request.user = user
        
        # Call the view
        response = shipment_list(request)
        
        print(f"✅ View returned status: {response.status_code}")
        
        # Check if response has shipments data
        if hasattr(response, 'context_data'):
            shipments = response.context_data.get('shipments', [])
            print(f"📊 Shipments in context: {len(shipments)}")
            
            if len(shipments) > 0:
                print("✅ Shipments data found!")
                first_shipment = shipments[0]
                print(f"    First shipment type: {type(first_shipment)}")
                print(f"    First shipment keys: {list(first_shipment.keys()) if isinstance(first_shipment, dict) else 'Not a dict'}")
                print(f"    First shipment client_name: {first_shipment.get('client_name', 'No client_name')}")
                print(f"    First shipment products: {len(first_shipment.get('products', []))}")
            else:
                print("❌ No shipments data found")
                
                # Check if there are any error messages
                messages = response.context_data.get('messages', [])
                if messages:
                    print("📝 Messages found:")
                    for message in messages:
                        print(f"    {message}")
        else:
            print("❌ No context_data in response")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing view: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_view_data()
