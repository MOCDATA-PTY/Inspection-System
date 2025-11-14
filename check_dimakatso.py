#!/usr/bin/env python3
"""
Script to check Dimakatso's inspector ID and any inspections linked to him
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import InspectorMapping, FoodSafetyAgencyInspection

if __name__ == '__main__':
    print("=" * 100)
    print("CHECKING DIMAKATSO'S INSPECTOR ID AND INSPECTIONS")
    print("=" * 100)
    print()
    
    # Find Dimakatso user
    try:
        user = User.objects.get(username__iexact='Dimakatso')
        full_name = user.get_full_name()
        print(f"✅ Found User:")
        print(f"   Username: {user.username}")
        print(f"   Full Name: {full_name}")
        print(f"   Email: {user.email or 'N/A'}")
        print(f"   Role: {getattr(user, 'role', 'N/A')}")
        print(f"   Active: {user.is_active}")
        print()
    except User.DoesNotExist:
        print("❌ User 'Dimakatso' not found")
        print()
        # Try to find similar
        users = User.objects.filter(username__icontains='dimakatso')
        if users.exists():
            user = users.first()
            full_name = user.get_full_name()
            print(f"Found similar user: {user.username} ({full_name})")
        else:
            print("No users found with 'dimakatso' in username")
            exit(1)
    
    # Check InspectorMapping
    print("=" * 100)
    print("INSPECTOR MAPPING")
    print("=" * 100)
    print()
    
    inspector_mapping = InspectorMapping.objects.filter(
        inspector_name__icontains='Dimakatso'
    ).first()
    
    if inspector_mapping:
        inspector_id = inspector_mapping.inspector_id
        print(f"✅ Inspector Mapping Found:")
        print(f"   Inspector ID: {inspector_id}")
        print(f"   Inspector Name: {inspector_mapping.inspector_name}")
        print(f"   Is Active: {inspector_mapping.is_active}")
        print()
    else:
        # Try to find by full name
        inspector_mapping = InspectorMapping.objects.filter(
            inspector_name__iexact=full_name
        ).first()
        if inspector_mapping:
            inspector_id = inspector_mapping.inspector_id
            print(f"✅ Inspector Mapping Found (by full name):")
            print(f"   Inspector ID: {inspector_id}")
            print(f"   Inspector Name: {inspector_mapping.inspector_name}")
            print(f"   Is Active: {inspector_mapping.is_active}")
            print()
        else:
            print("❌ No Inspector Mapping found for Dimakatso")
            print("   This means Dimakatso does not have an inspector ID mapped yet")
            print()
            inspector_id = None
    
    # Check for inspections
    print("=" * 100)
    print("INSPECTIONS FOR DIMAKATSO")
    print("=" * 100)
    print()
    
    if inspector_id:
        # Search by inspector_id
        inspections_by_id = FoodSafetyAgencyInspection.objects.filter(
            inspector_id=inspector_id
        )
        
        # Also search by inspector_name (case-insensitive)
        inspections_by_name = FoodSafetyAgencyInspection.objects.filter(
            inspector_name__icontains='Dimakatso'
        )
        
        # Combine both queries (union)
        all_inspections = FoodSafetyAgencyInspection.objects.filter(
            inspector_id=inspector_id
        ) | FoodSafetyAgencyInspection.objects.filter(
            inspector_name__icontains='Dimakatso'
        )
        
        # Remove duplicates
        inspection_ids = set()
        unique_inspections = []
        for insp in all_inspections:
            if insp.id not in inspection_ids:
                inspection_ids.add(insp.id)
                unique_inspections.append(insp)
        
        print(f"Searching inspections by:")
        print(f"  - Inspector ID: {inspector_id}")
        print(f"  - Inspector Name containing 'Dimakatso'")
        print()
        
        if unique_inspections:
            print(f"✅ Found {len(unique_inspections)} inspection(s) for Dimakatso:")
            print()
            
            for i, inspection in enumerate(unique_inspections[:20], 1):  # Show first 20
                print(f"{i}. Inspection ID: {inspection.id}")
                print(f"   Remote ID: {inspection.remote_id or 'N/A'}")
                print(f"   Date: {inspection.date_of_inspection or 'N/A'}")
                print(f"   Client: {inspection.client_name or 'N/A'}")
                print(f"   Commodity: {inspection.commodity or 'N/A'}")
                print(f"   Product: {inspection.product_name or 'N/A'}")
                print(f"   Inspector ID (from inspection): {inspection.inspector_id}")
                print(f"   Inspector Name (from inspection): {inspection.inspector_name}")
                print()
            
            if len(unique_inspections) > 20:
                print(f"   ... and {len(unique_inspections) - 20} more inspections")
                print()
            
            # Summary statistics
            print("=" * 100)
            print("SUMMARY STATISTICS")
            print("=" * 100)
            print()
            
            total_count = len(unique_inspections)
            print(f"Total Inspections: {total_count}")
            
            # Count by commodity
            commodity_counts = {}
            for insp in unique_inspections:
                commodity = insp.commodity or 'Unknown'
                commodity_counts[commodity] = commodity_counts.get(commodity, 0) + 1
            
            print("\nBy Commodity:")
            for commodity, count in sorted(commodity_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {commodity}: {count}")
            
        else:
            print("❌ No inspections found for Dimakatso")
            print()
            print("This could mean:")
            print("  1. Dimakatso hasn't performed any inspections yet")
            print("  2. The inspections haven't been synced from the remote system")
            print("  3. The inspector_id in the inspection data doesn't match Dimakatso's ID")
            print()
            
            # Check if there are any inspections with similar inspector names
            print("Checking for similar inspector names in inspection data...")
            similar_names = FoodSafetyAgencyInspection.objects.values_list(
                'inspector_name', flat=True
            ).distinct()
            
            similar = [name for name in similar_names if name and 'dimakatso' in name.lower()]
            if similar:
                print(f"Found similar names: {similar}")
            else:
                print("No similar inspector names found in inspection data")
    else:
        print("❌ Cannot check inspections - no inspector ID found")
        print()
        print("To link inspections to Dimakatso:")
        print("  1. Dimakatso needs an InspectorMapping entry with the correct inspector_id")
        print("  2. The inspector_id should match the InspectorId from the remote SQL Server")
        print("  3. Once mapped, inspections will be linked by inspector_id")
    
    print()
    print("=" * 100)

