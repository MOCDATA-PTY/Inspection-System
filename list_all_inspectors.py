#!/usr/bin/env python3
"""
List all unique inspectors from the inspection database
Shows inspector names and their inspection counts
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def list_all_inspectors():
    """List all unique inspectors with their inspection counts"""
    print("👥 All Unique Inspectors in the System")
    print("=" * 80)
    
    from main.models import FoodSafetyAgencyInspection
    from django.db.models import Count, Q
    
    # Get all unique inspectors with their inspection counts
    inspectors = FoodSafetyAgencyInspection.objects.values('inspector_name', 'inspector_id').annotate(
        inspection_count=Count('id'),
        recent_inspections=Count('id', filter=Q(date_of_inspection__gte='2025-01-01'))
    ).exclude(
        inspector_name__isnull=True
    ).exclude(
        inspector_name=''
    ).order_by('-inspection_count')
    
    print(f"📊 Found {len(inspectors)} unique inspectors\n")
    
    # Display inspectors with their stats
    for i, inspector in enumerate(inspectors, 1):
        inspector_name = inspector['inspector_name']
        inspector_id = inspector['inspector_id']
        total_count = inspector['inspection_count']
        recent_count = inspector['recent_inspections']
        
        print(f"{i:2d}. {inspector_name}")
        print(f"    Inspector ID: {inspector_id}")
        print(f"    Total Inspections: {total_count:,}")
        print(f"    Recent Inspections (2025): {recent_count:,}")
        print()
    
    # Summary statistics
    total_inspections = sum(inspector['inspection_count'] for inspector in inspectors)
    total_recent = sum(inspector['recent_inspections'] for inspector in inspectors)
    
    print("=" * 80)
    print("📈 SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Total Unique Inspectors: {len(inspectors)}")
    print(f"Total Inspections: {total_inspections:,}")
    print(f"Total Recent Inspections (2025): {total_recent:,}")
    
    # Top 10 most active inspectors
    print(f"\n🏆 TOP 10 MOST ACTIVE INSPECTORS:")
    print("-" * 50)
    for i, inspector in enumerate(inspectors[:10], 1):
        print(f"{i:2d}. {inspector['inspector_name']} - {inspector['inspection_count']:,} inspections")
    
    # Inspectors with recent activity
    recent_active = [insp for insp in inspectors if insp['recent_inspections'] > 0]
    print(f"\n📅 INSPECTORS WITH 2025 ACTIVITY ({len(recent_active)}):")
    print("-" * 50)
    for i, inspector in enumerate(recent_active, 1):
        print(f"{i:2d}. {inspector['inspector_name']} - {inspector['recent_inspections']:,} recent inspections")

def list_inspectors_by_commodity():
    """List inspectors grouped by commodity type"""
    print("\n\n🏷️ Inspectors by Commodity Type")
    print("=" * 80)
    
    from main.models import FoodSafetyAgencyInspection
    from django.db.models import Count, Q
    
    commodities = FoodSafetyAgencyInspection.objects.values_list('commodity', flat=True).distinct().exclude(commodity__isnull=True).exclude(commodity='')
    
    for commodity in sorted(commodities):
        print(f"\n📦 {commodity.upper()} INSPECTORS:")
        print("-" * 40)
        
        commodity_inspectors = FoodSafetyAgencyInspection.objects.filter(
            commodity__iexact=commodity
        ).values('inspector_name').annotate(
            count=Count('id')
        ).exclude(
            inspector_name__isnull=True
        ).exclude(
            inspector_name=''
        ).order_by('-count')
        
        for i, inspector in enumerate(commodity_inspectors, 1):
            print(f"{i:2d}. {inspector['inspector_name']} - {inspector['count']} inspections")

if __name__ == "__main__":
    try:
        list_all_inspectors()
        list_inspectors_by_commodity()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
