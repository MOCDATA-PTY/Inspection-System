#!/usr/bin/env python
"""
Test script to verify compliance status display in grouped headers
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from main.views.core_views import check_compliance_documents_status

def test_compliance_status_display():
    print("Testing Compliance Status Display in Grouped Headers")
    print("=" * 60)
    
    # Test with Django test client
    client = Client()
    
    # Login as developer
    login_success = client.login(username='developer', password='XHnj1C#QkFs9')
    if not login_success:
        print("FAILED: Could not login as developer")
        return False
    
    print("SUCCESS: Logged in as developer")
    
    # Get the inspections page
    response = client.get('/inspections/')
    if response.status_code != 200:
        print(f"FAILED: Could not access inspections page (status: {response.status_code})")
        return False
    
    print("SUCCESS: Accessed inspections page")
    
    # Check if compliance status indicators are in the response
    content = response.content.decode('utf-8')
    
    # Look for compliance status indicators
    compliant_count = content.count('Compliant')
    partial_count = content.count('Partial')
    non_compliant_count = content.count('Non-Compliant')
    
    print(f"📊 Compliance Status Indicators Found:")
    print(f"   Compliant: {compliant_count}")
    print(f"   Partial: {partial_count}")
    print(f"   Non-Compliant: {non_compliant_count}")
    
    if compliant_count > 0 or partial_count > 0 or non_compliant_count > 0:
        print("SUCCESS: Compliance status indicators are present in the template")
        
        # Show some examples
        lines = content.split('\n')
        compliance_lines = [line for line in lines if 'Compliant' in line or 'Partial' in line or 'Non-Compliant' in line]
        
        print(f"\n📋 Sample compliance status lines found:")
        for i, line in enumerate(compliance_lines[:5]):  # Show first 5 examples
            print(f"   {i+1}. {line.strip()}")
        
        return True
    else:
        print("FAILED: No compliance status indicators found in the template")
        return False

def test_compliance_status_logic():
    print("\n" + "=" * 60)
    print("Testing Compliance Status Logic")
    print("=" * 60)
    
    # Get some sample inspections
    inspections = FoodSafetyAgencyInspection.objects.all()[:5]
    
    for inspection in inspections:
        print(f"\n🔍 Testing inspection: {inspection.client_name} on {inspection.date_of_inspection}")
        
        # Get all inspections for this client and date
        group_inspections = FoodSafetyAgencyInspection.objects.filter(
            client_name=inspection.client_name,
            date_of_inspection=inspection.date_of_inspection
        )
        
        print(f"   Group size: {len(group_inspections)} inspections")
        
        # Test compliance status check
        try:
            compliance_status = check_compliance_documents_status(
                group_inspections, 
                inspection.client_name, 
                inspection.date_of_inspection
            )
            
            print(f"   Compliance result: {compliance_status}")
            
            # Determine the status that would be shown
            has_any_compliance = compliance_status.get('has_any_compliance', False)
            all_commodities_have_compliance = compliance_status.get('all_commodities_have_compliance', False)
            
            if all_commodities_have_compliance:
                display_status = "Compliant"
            elif has_any_compliance:
                display_status = "Partial"
            else:
                display_status = "Non-Compliant"
                
            print(f"   Display status: {display_status}")
            
        except Exception as e:
            print(f"   ERROR: Error checking compliance: {e}")

if __name__ == "__main__":
    print("Starting compliance status display test...")
    
    # Test the template display
    success = test_compliance_status_display()
    
    # Test the logic
    test_compliance_status_logic()
    
    if success:
        print("\nSUCCESS: Compliance status display is working!")
    else:
        print("\nFAILED: Compliance status display needs fixing")
