#!/usr/bin/env python3
"""
Test script to verify KM and Hours endpoints with proper authentication
"""

import requests
import json
from django.test import Client
from django.contrib.auth.models import User
import os
import sys
import django

# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

def test_with_django_client():
    """Test endpoints using Django test client"""
    
    print("🧪 Testing KM and Hours Endpoints with Django Test Client")
    print("=" * 60)
    
    # Create test client
    client = Client()
    
    # Create or get a test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        print("   Created test user: testuser")
    
    # Login the user
    login_success = client.login(username='testuser', password='testpass')
    print(f"   Login successful: {login_success}")
    
    if not login_success:
        print("   ❌ Failed to login test user")
        return False
    
    # Get a sample inspection
    inspection = FoodSafetyAgencyInspection.objects.first()
    if not inspection:
        print("   ❌ No inspections found in database")
        return False
    
    print(f"   Using inspection: {inspection.client_name} on {inspection.date_of_inspection}")
    
    # Create test group ID
    client_name = inspection.client_name.replace(' ', '_').replace('-', '_')
    date_str = inspection.date_of_inspection.strftime('%Y%m%d')
    test_group_id = f"{client_name}_{date_str}"
    
    print(f"   Test Group ID: {test_group_id}")
    
    # Test KM update
    print("\n1. Testing KM update...")
    km_data = {
        'group_id': test_group_id,
        'km_traveled': '40.0'
    }
    
    response = client.post('/update-group-km-traveled/', data=km_data)
    print(f"   Response Status: {response.status_code}")
    print(f"   Response Content: {response.content.decode()}")
    
    if response.status_code == 200:
        try:
            response_data = json.loads(response.content)
            print(f"   Response JSON: {response_data}")
            if response_data.get('success'):
                print("   ✅ KM update successful")
            else:
                print(f"   ❌ KM update failed: {response_data.get('error')}")
        except json.JSONDecodeError:
            print("   ❌ Invalid JSON response")
    else:
        print(f"   ❌ HTTP error: {response.status_code}")
    
    # Test Hours update
    print("\n2. Testing Hours update...")
    hours_data = {
        'group_id': test_group_id,
        'hours': '5.0'
    }
    
    response = client.post('/update-group-hours/', data=hours_data)
    print(f"   Response Status: {response.status_code}")
    print(f"   Response Content: {response.content.decode()}")
    
    if response.status_code == 200:
        try:
            response_data = json.loads(response.content)
            print(f"   Response JSON: {response_data}")
            if response_data.get('success'):
                print("   ✅ Hours update successful")
            else:
                print(f"   ❌ Hours update failed: {response_data.get('error')}")
        except json.JSONDecodeError:
            print("   ❌ Invalid JSON response")
    else:
        print(f"   ❌ HTTP error: {response.status_code}")
    
    # Verify the updates in database
    print("\n3. Verifying database updates...")
    updated_inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name=inspection.client_name,
        date_of_inspection=inspection.date_of_inspection
    )
    
    for insp in updated_inspections:
        print(f"   Inspection {insp.id}: KM={insp.km_traveled}, Hours={insp.hours}")
    
    return True

def test_group_id_parsing():
    """Test the group ID parsing logic"""
    
    print("\n🔍 Testing Group ID Parsing Logic")
    print("=" * 40)
    
    # Test various group ID formats
    test_cases = [
        "Boxer_Superstore___Kwamashu_2_20250926",
        "Test_Client_20250926",
        "Client_With_Spaces_20250926",
        "Simple_20250926"
    ]
    
    for group_id in test_cases:
        print(f"\n   Testing Group ID: {group_id}")
        
        try:
            if '_' not in group_id:
                print("   ❌ Invalid group ID format")
                continue
            
            parts = group_id.split('_')
            if len(parts) < 2:
                print("   ❌ Invalid group ID format")
                continue
            
            # Reconstruct client_name and date
            date_part = parts[-1]
            client_name_parts = parts[:-1]
            client_name = '_'.join(client_name_parts)
            
            print(f"   Parsed Client Name: {client_name}")
            print(f"   Parsed Date Part: {date_part}")
            
            # Convert date string to date object
            from datetime import datetime
            date_of_inspection = None
            for fmt in ('%Y-%m-%d', '%Y%m%d'):
                try:
                    date_of_inspection = datetime.strptime(date_part, fmt).date()
                    break
                except ValueError:
                    continue
            
            if not date_of_inspection:
                print(f"   ❌ Invalid date format: {date_part}")
                continue
            
            print(f"   Parsed Date: {date_of_inspection}")
            
            # Test normalization
            import re
            def normalize(n):
                return re.sub(r'[^a-zA-Z0-9]', '', (n or '')).lower()
            
            raw_key = normalize(client_name)
            print(f"   Normalized Key: {raw_key}")
            
            # Find matching inspections
            candidate_qs = FoodSafetyAgencyInspection.objects.filter(
                date_of_inspection=date_of_inspection
            )
            matching_ids = [ins.id for ins in candidate_qs if normalize(ins.client_name) == raw_key]
            inspections = FoodSafetyAgencyInspection.objects.filter(id__in=matching_ids)
            
            print(f"   Found {inspections.count()} matching inspections")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Main test function"""
    
    print("🚀 Authenticated Endpoint Tests")
    print("=" * 60)
    
    # Test with Django client
    success = test_with_django_client()
    
    # Test group ID parsing
    test_group_id_parsing()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Tests completed successfully")
    else:
        print("❌ Some tests failed")
    
    return success

if __name__ == "__main__":
    main()
