#!/usr/bin/env python3
"""
Test Master Service Control without Toggle
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_master_control_no_toggle():
    """Test the master service control functionality without toggle."""
    print("🧪 Testing Master Service Control (No Toggle)")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    # Create a test user if it doesn't exist
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print("✅ Created test user")
    else:
        print("✅ Test user already exists")
    
    # Set user role to developer
    test_user.role = 'developer'
    test_user.save()
    print("✅ Set user role to developer")
    
    # Login
    login_success = client.login(username='testuser', password='testpass123')
    if not login_success:
        print("❌ Failed to login")
        return False
    
    print("✅ Successfully logged in")
    
    # Test master service control status endpoint
    print("\n📊 Testing Master Service Control Status...")
    response = client.get('/master-service/status/')
    print(f"Status endpoint response: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status endpoint working")
        print(f"   Services found: {data.get('total_services', 0)}")
        print(f"   Running services: {data.get('running_services', 0)}")
        print(f"   All running: {data.get('all_running', False)}")
        print(f"   Any running: {data.get('any_running', False)}")
    else:
        print(f"❌ Status endpoint failed: {response.status_code}")
        return False
    
    # Test start all services endpoint
    print("\n🚀 Testing Start All Services...")
    response = client.post('/master-service/start-all/')
    print(f"Start all services response: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Start all services endpoint working")
        print(f"   Success: {data.get('success', False)}")
        print(f"   Message: {data.get('message', 'No message')}")
        
        if 'results' in data:
            print("   Service results:")
            for service, result in data['results'].items():
                print(f"     {service}: {result}")
    else:
        print(f"❌ Start all services failed: {response.status_code}")
        print(f"   Response: {response.content.decode()}")
    
    # Test stop all services endpoint
    print("\n🛑 Testing Stop All Services...")
    response = client.post('/master-service/stop-all/')
    print(f"Stop all services response: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Stop all services endpoint working")
        print(f"   Success: {data.get('success', False)}")
        print(f"   Message: {data.get('message', 'No message')}")
        
        if 'results' in data:
            print("   Service results:")
            for service, result in data['results'].items():
                print(f"     {service}: {result}")
    else:
        print(f"❌ Stop all services failed: {response.status_code}")
        print(f"   Response: {response.content.decode()}")
    
    # Test settings page without toggle
    print("\n⚙️ Testing Settings Page (No Toggle)...")
    response = client.get('/settings/')
    print(f"Settings page response: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for master service control elements (without toggle)
        checks = [
            ('Master Service Control', 'Master Service Control' in content),
            ('Start All Services', 'Start All Services' in content),
            ('Stop All Services', 'Stop All Services' in content),
            ('Refresh Status', 'Refresh Status' in content),
            ('startAllServices', 'startAllServices' in content),
            ('stopAllServices', 'stopAllServices' in content),
            ('refreshServiceStatus', 'refreshServiceStatus' in content),
            ('Service Results', 'Service Results' in content),
        ]
        
        # Check that toggle is NOT present
        toggle_checks = [
            ('master_service_control', 'master_service_control' not in content),
            ('handleMasterServiceControl', 'handleMasterServiceControl' not in content),
            ('switch', 'switch' not in content or content.count('switch') < 3),  # Should have fewer switches now
        ]
        
        print("   Master Service Control Elements (Should be present):")
        for check_name, found in checks:
            status = "✅" if found else "❌"
            print(f"     {status} {check_name}: {found}")
        
        print("   Toggle Elements (Should NOT be present):")
        for check_name, not_present in toggle_checks:
            status = "✅" if not_present else "❌"
            print(f"     {status} {check_name}: {'Not present' if not_present else 'Still present'}")
        
        if all(found for _, found in checks) and all(not_present for _, not_present in toggle_checks):
            print("✅ Master Service Control (No Toggle) is properly implemented!")
            return True
        else:
            print("⚠️ Some Master Service Control elements missing or toggle still present")
            return False
    else:
        print(f"❌ Settings page failed: {response.status_code}")
        return False

if __name__ == "__main__":
    success = test_master_control_no_toggle()
    if success:
        print("\n✅ Master Service Control (No Toggle) test completed successfully!")
    else:
        print("\n❌ Master Service Control (No Toggle) test failed!")


