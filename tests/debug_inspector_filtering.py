#!/usr/bin/env python3
"""
Debug inspector filtering step by step
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, InspectorMapping
from django.contrib.auth.models import User
from datetime import datetime, timedelta

def debug_inspector_filtering():
    """Debug inspector filtering step by step"""
    print("🔍 Debugging inspector filtering...")
    
    try:
        # Get test user
        user = User.objects.get(username='testuser')
        print(f"👤 User: {user.username}")
        print(f"    Full name: {user.get_full_name()}")
        print(f"    Role: {user.role}")
        
        # Get inspector mapping
        mapping = InspectorMapping.objects.get(
            inspector_name=user.get_full_name() or user.username
        )
        inspector_id = mapping.inspector_id
        print(f"📋 Inspector ID: {inspector_id}")
        
        # Step 1: Get all inspections
        all_inspections = FoodSafetyAgencyInspection.objects.all()
        print(f"📊 Step 1 - All inspections: {all_inspections.count()}")
        
        # Step 2: Filter by date (last 6 months)
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_inspections = all_inspections.filter(date_of_inspection__gte=six_months_ago)
        print(f"📊 Step 2 - Recent inspections: {recent_inspections.count()}")
        
        # Step 3: Filter by inspector ID
        inspector_inspections = recent_inspections.filter(inspector_id=inspector_id)
        print(f"📊 Step 3 - Inspector inspections: {inspector_inspections.count()}")
        
        if inspector_inspections.count() > 0:
            print("✅ Found inspections for this inspector!")
            
            # Show sample inspections
            samples = inspector_inspections[:3]
            print("📋 Sample inspections:")
            for inspection in samples:
                print(f"    {inspection.client_name} - {inspection.date_of_inspection}")
                
            # Check grouping
            from django.db.models import Count
            groups = inspector_inspections.values(
                'client_name', 
                'date_of_inspection'
            ).annotate(
                inspection_count=Count('id')
            ).order_by('-date_of_inspection', 'client_name')
            
            print(f"📊 Step 4 - Groups: {groups.count()}")
            
            if groups.count() > 0:
                print("✅ Found groups!")
                for group in groups[:3]:
                    print(f"    {group['client_name']} - {group['date_of_inspection']} ({group['inspection_count']} inspections)")
            else:
                print("❌ No groups found")
        else:
            print("❌ No inspections found for this inspector")
            
            # Check what inspector IDs exist in recent data
            recent_inspector_ids = recent_inspections.values_list('inspector_id', flat=True).distinct()[:10]
            print(f"📊 Recent inspector IDs: {list(recent_inspector_ids)}")
            
        return inspector_inspections.count() > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_inspector_filtering()
