#!/usr/bin/env python3
"""
Check inspections for inspector ID 9023
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
from datetime import datetime, timedelta

def check_inspector_inspections():
    """Check inspections for inspector ID 9023"""
    print("🔍 Checking inspections for inspector ID 9023...")
    
    try:
        # Check total inspections for this inspector
        total_inspections = FoodSafetyAgencyInspection.objects.filter(inspector_id=9023).count()
        print(f"📊 Total inspections for inspector ID 9023: {total_inspections}")
        
        if total_inspections > 0:
            # Get a sample inspection
            sample = FoodSafetyAgencyInspection.objects.filter(inspector_id=9023).first()
            print(f"📋 Sample inspection:")
            print(f"    Client: {sample.client_name}")
            print(f"    Date: {sample.date_of_inspection}")
            print(f"    Inspector: {sample.inspector_name}")
            print(f"    Inspector ID: {sample.inspector_id}")
            
            # Check recent inspections (last 6 months)
            six_months_ago = datetime.now() - timedelta(days=180)
            recent_inspections = FoodSafetyAgencyInspection.objects.filter(
                inspector_id=9023,
                date_of_inspection__gte=six_months_ago
            ).count()
            print(f"📅 Recent inspections (last 6 months): {recent_inspections}")
            
            if recent_inspections > 0:
                print("✅ Found recent inspections!")
                
                # Show some recent inspections
                recent = FoodSafetyAgencyInspection.objects.filter(
                    inspector_id=9023,
                    date_of_inspection__gte=six_months_ago
                ).order_by('-date_of_inspection')[:5]
                
                print("📋 Recent inspections:")
                for inspection in recent:
                    print(f"    {inspection.client_name} - {inspection.date_of_inspection}")
            else:
                print("❌ No recent inspections found")
                
                # Check older inspections
                older_inspections = FoodSafetyAgencyInspection.objects.filter(
                    inspector_id=9023,
                    date_of_inspection__lt=six_months_ago
                ).count()
                print(f"📅 Older inspections: {older_inspections}")
        else:
            print("❌ No inspections found for this inspector ID")
            
            # Check what inspector IDs exist
            all_inspector_ids = FoodSafetyAgencyInspection.objects.values_list('inspector_id', flat=True).distinct()[:10]
            print(f"📊 Sample inspector IDs in database: {list(all_inspector_ids)}")
            
        return total_inspections > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_inspector_inspections()
