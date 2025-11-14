#!/usr/bin/env python3
"""
Script to check what inspector IDs exist in inspection data and find Dimakatso's real ID
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Count, Q

if __name__ == '__main__':
    print("=" * 100)
    print("CHECKING INSPECTION DATA FOR DIMAKATSO")
    print("=" * 100)
    print()
    
    # Check all unique inspector IDs in inspection data
    print("All unique Inspector IDs in inspection data:")
    print("-" * 100)
    
    inspector_ids = FoodSafetyAgencyInspection.objects.exclude(
        inspector_id__isnull=True
    ).values('inspector_id').annotate(
        count=Count('inspector_id')
    ).order_by('inspector_id')
    
    print(f"Total unique inspector IDs: {inspector_ids.count()}")
    print()
    
    # Show first 30 inspector IDs
    for item in inspector_ids[:30]:
        inspector_id = item['inspector_id']
        count = item['count']
        # Get inspector name for this ID
        sample_insp = FoodSafetyAgencyInspection.objects.filter(
            inspector_id=inspector_id
        ).first()
        inspector_name = sample_insp.inspector_name if sample_insp else 'Unknown'
        print(f"  Inspector ID {inspector_id:4d}: {inspector_name:30s} ({count} inspections)")
    
    if inspector_ids.count() > 30:
        print(f"  ... and {inspector_ids.count() - 30} more")
    
    print()
    print("=" * 100)
    print("SEARCHING FOR DIMAKATSO/MODIBA IN INSPECTION DATA")
    print("=" * 100)
    print()
    
    # Search for any mentions of Dimakatso or Modiba
    dimakatso_inspections = FoodSafetyAgencyInspection.objects.filter(
        Q(inspector_name__icontains='Dimakatso') |
        Q(inspector_name__icontains='dimakatso') |
        Q(inspector_name__icontains='MODIBA') |
        Q(inspector_name__icontains='Modiba')
    )
    
    if dimakatso_inspections.exists():
        print(f"✅ Found {dimakatso_inspections.count()} inspection(s) with Dimakatso/Modiba in name:")
        print()
        
        # Get unique inspector IDs and names
        unique_combos = dimakatso_inspections.values('inspector_id', 'inspector_name').distinct()
        
        for combo in unique_combos:
            inspector_id = combo['inspector_id']
            inspector_name = combo['inspector_name']
            count = dimakatso_inspections.filter(
                inspector_id=inspector_id,
                inspector_name=inspector_name
            ).count()
            
            print(f"  Inspector ID: {inspector_id}")
            print(f"  Inspector Name: {inspector_name}")
            print(f"  Number of inspections: {count}")
            print()
    else:
        print("❌ No inspections found with 'Dimakatso' or 'Modiba' in inspector name")
        print()
    
    # Check for LERATO MODIBA (which exists in the map)
    print("=" * 100)
    print("CHECKING FOR LERATO MODIBA (Inspector ID 160)")
    print("=" * 100)
    print()
    
    lerato_inspections = FoodSafetyAgencyInspection.objects.filter(
        Q(inspector_id=160) |
        Q(inspector_name__icontains='LERATO MODIBA') |
        Q(inspector_name__icontains='Lerato Modiba')
    )
    
    if lerato_inspections.exists():
        print(f"✅ Found {lerato_inspections.count()} inspection(s) for LERATO MODIBA (ID: 160)")
        print("   Note: This might be a different person (same last name)")
    else:
        print("❌ No inspections found for LERATO MODIBA (ID: 160)")
    
    print()
    print("=" * 100)
    print("RECOMMENDATION")
    print("=" * 100)
    print()
    print("To link inspections to Dimakatso:")
    print("1. Check the remote SQL Server for Dimakatso's actual Inspector ID")
    print("2. Update the InspectorMapping to use the correct inspector_id")
    print("3. Add Dimakatso to the INSPECTOR_NAME_MAP in main/views/data_views.py")
    print("4. Re-sync inspections from the remote system")
    print()
    print("Current Inspector ID (9107) appears to be auto-generated and not in the remote system")
    print()

