#!/usr/bin/env python3
"""
Check if there are inspections in the database
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

def check_inspections():
    """Check if there are inspections in the database"""
    print("🔍 Checking inspections in database...")
    
    try:
        total_inspections = FoodSafetyAgencyInspection.objects.count()
        print(f"📊 Total inspections in database: {total_inspections}")
        
        if total_inspections > 0:
            # Get a sample inspection
            sample = FoodSafetyAgencyInspection.objects.first()
            print(f"📋 Sample inspection:")
            print(f"    Client: {sample.client_name}")
            print(f"    Date: {sample.date_of_inspection}")
            print(f"    Inspector: {sample.inspector_name}")
            print(f"    Product: {sample.product_name}")
            
            # Check recent inspections (last 6 months)
            from datetime import datetime, timedelta
            six_months_ago = datetime.now() - timedelta(days=180)
            recent_inspections = FoodSafetyAgencyInspection.objects.filter(
                date_of_inspection__gte=six_months_ago
            ).count()
            print(f"📅 Recent inspections (last 6 months): {recent_inspections}")
            
            if recent_inspections == 0:
                print("❌ No recent inspections found - this is why the page is empty!")
                print("💡 The view filters to only show inspections from the last 6 months")
                
                # Show some older inspections
                older_inspections = FoodSafetyAgencyInspection.objects.filter(
                    date_of_inspection__lt=six_months_ago
                ).count()
                print(f"📅 Older inspections: {older_inspections}")
                
                if older_inspections > 0:
                    print("💡 There are older inspections, but they're filtered out by the view")
        else:
            print("❌ No inspections found in database at all!")
            
        return total_inspections > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_inspections()
