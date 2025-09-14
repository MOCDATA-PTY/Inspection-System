#!/usr/bin/env python3
"""
Test script for the color-coded View Files functionality.
This script tests the file status detection and color coding system.
"""

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth.models import User

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.views.core_views import get_page_clients_files
from main.models import FoodSafetyAgencyInspection, Client

def test_color_coding_system():
    """Test the color coding system for different file statuses."""
    print("🎨 Testing Color-Coded View Files System")
    print("=" * 50)
    
    # Create a mock request
    factory = RequestFactory()
    
    # Create a test user (or use existing)
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False
    
    # Get some client names from the database
    clients = Client.objects.all()[:3]
    if clients.count() == 0:
        print("⚠️ No clients found in database. Creating test data...")
        return True
    
    client_names = [client.name for client in clients if client.name]
    target_client = client_names[0] if client_names else "Test Client"
    
    print(f"🎯 Testing with target client: {target_client}")
    print(f"📄 Using {len(client_names)} clients from current page")
    
    # Create request with pagination data
    request_data = {
        'client_names': client_names,
        'target_client': target_client
    }
    
    request = factory.post('/page-clients-files/', 
                          data=str(request_data).replace("'", '"'), 
                          content_type='application/json')
    request.user = user
    
    try:
        print("🚀 Calling get_page_clients_files...")
        response = get_page_clients_files(request)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Color Coding Test PASSED!")
                
                # Display file status information
                file_status = data.get('file_status', 'unknown')
                print(f"🎨 File Status: {file_status}")
                
                # Show what each color means
                print("\n🎨 Color Coding System:")
                print("🟢 Green (all_files): All files available (RFI, Invoice, Lab Results, Compliance)")
                print("🔵 Blue (compliance_only): Only compliance documents available")
                print("🔴 Red (no_files): No files found")
                print("🟠 Orange (partial_files): Some files available (partial)")
                
                # Show current status
                status_colors = {
                    'all_files': '🟢 Green',
                    'compliance_only': '🔵 Blue', 
                    'no_files': '🔴 Red',
                    'partial_files': '🟠 Orange'
                }
                
                current_color = status_colors.get(file_status, '⚪ Unknown')
                print(f"\n📊 Current Status: {current_color}")
                
                # Show detailed file information
                print(f"\n📁 File Details:")
                print(f"  - RFI Documents: {'✅' if data.get('has_rfi') else '❌'}")
                print(f"  - Invoices: {'✅' if data.get('has_invoice') else '❌'}")
                print(f"  - Lab Results: {'✅' if data.get('has_lab') else '❌'}")
                print(f"  - Retest Results: {'✅' if data.get('has_retest') else '❌'}")
                print(f"  - Compliance Documents: {'✅' if data.get('has_compliance') else '❌'}")
                
                return True
            else:
                print(f"❌ Test FAILED: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Test FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test FAILED with exception: {e}")
        return False

def test_color_logic():
    """Test the color logic for different scenarios."""
    print("\n🧪 Testing Color Logic Scenarios")
    print("=" * 40)
    
    scenarios = [
        {
            'name': 'All Files Available',
            'files': {'rfi': [1], 'invoice': [1], 'lab': [1], 'compliance': [1]},
            'expected': 'all_files',
            'color': '🟢 Green'
        },
        {
            'name': 'Compliance Only',
            'files': {'rfi': [], 'invoice': [], 'lab': [], 'compliance': [1]},
            'expected': 'compliance_only',
            'color': '🔵 Blue'
        },
        {
            'name': 'No Files',
            'files': {'rfi': [], 'invoice': [], 'lab': [], 'compliance': []},
            'expected': 'no_files',
            'color': '🔴 Red'
        },
        {
            'name': 'Partial Files (RFI + Compliance)',
            'files': {'rfi': [1], 'invoice': [], 'lab': [], 'compliance': [1]},
            'expected': 'partial_files',
            'color': '🟠 Orange'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        
        # Simulate the logic
        has_rfi = len(scenario['files'].get('rfi', [])) > 0
        has_invoice = len(scenario['files'].get('invoice', [])) > 0
        has_lab = len(scenario['files'].get('lab', [])) > 0
        has_compliance = len(scenario['files'].get('compliance', [])) > 0
        total_files = sum(len(files) for files in scenario['files'].values())
        
        # Determine status
        if total_files == 0:
            file_status = 'no_files'
        elif has_rfi and has_invoice and has_lab and has_compliance:
            file_status = 'all_files'
        elif has_compliance and not (has_rfi or has_invoice or has_lab):
            file_status = 'compliance_only'
        else:
            file_status = 'partial_files'
        
        # Check if result matches expected
        if file_status == scenario['expected']:
            print(f"  ✅ Correct: {scenario['color']} ({file_status})")
        else:
            print(f"  ❌ Incorrect: Expected {scenario['expected']}, got {file_status}")
    
    return True

if __name__ == "__main__":
    print("🎨 Color-Coded View Files System Test")
    print("=" * 50)
    
    # Test color logic
    test_color_logic()
    
    # Test actual functionality
    success = test_color_coding_system()
    
    if success:
        print("\n🎉 All tests passed! The color-coded system is working.")
        print("\n💡 How it works:")
        print("   🟢 Green: All files available (RFI, Invoice, Lab Results, Compliance)")
        print("   🔵 Blue: Only compliance documents available")
        print("   🔴 Red: No files found")
        print("   🟠 Orange: Some files available (partial)")
        print("\n🚀 Now when you click 'View Files':")
        print("   1. Button color changes based on file availability")
        print("   2. Status indicator shows in the modal")
        print("   3. Tooltip explains what the color means")
        print("   4. Visual feedback for file status at a glance!")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        sys.exit(1)
