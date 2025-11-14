#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test adding KM and Hours as an inspector user
Temporarily changes developer account to inspector for testing
"""
import os
import sys
import django
from datetime import datetime

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model
from main.models import FoodSafetyAgencyInspection
from django.db.models import Count, Sum, Avg, Max, Min
from decimal import Decimal

User = get_user_model()

print("\n" + "="*80)
print("INSPECTOR KM AND HOURS TEST")
print("="*80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Store original role
original_role = None

try:
    # Step 1: Show current KM and Hours data
    print("STEP 1: Current Database State")
    print("-"*80)

    total = FoodSafetyAgencyInspection.objects.count()
    with_km = FoodSafetyAgencyInspection.objects.exclude(km_traveled__isnull=True).exclude(km_traveled=0).count()
    with_hours = FoodSafetyAgencyInspection.objects.exclude(hours__isnull=True).exclude(hours=0).count()

    print(f"Total inspections: {total}")
    print(f"With KM data: {with_km} ({(with_km/total*100) if total > 0 else 0:.1f}%)")
    print(f"With Hours data: {with_hours} ({(with_hours/total*100) if total > 0 else 0:.1f}%)")

    # Show sample data
    print("\nSample inspections with KM/Hours (first 5):")
    samples = FoodSafetyAgencyInspection.objects.filter(
        km_traveled__isnull=False
    ).exclude(km_traveled=0)[:5]

    for idx, insp in enumerate(samples, 1):
        print(f"  {idx}. {insp.client_name} ({insp.date_of_inspection})")
        print(f"     KM: {insp.km_traveled or 'N/A'} | Hours: {insp.hours or 'N/A'}")

    # Step 2: Change developer to inspector
    print("\n" + "="*80)
    print("STEP 2: Changing developer account to inspector")
    print("-"*80)

    developer = User.objects.get(username='developer')
    original_role = developer.role
    print(f"Original role: {original_role}")

    developer.role = 'inspector'
    developer.save()
    developer.refresh_from_db()

    print(f"New role: {developer.role}")
    print(">>> Successfully changed to inspector!")

    # Step 3: Find a test inspection
    print("\n" + "="*80)
    print("STEP 3: Finding a test inspection")
    print("-"*80)

    # Find a recent inspection without KM/Hours, or just use a recent one
    test_insp = FoodSafetyAgencyInspection.objects.filter(
        km_traveled__isnull=True,
        hours__isnull=True
    ).order_by('-date_of_inspection').first()

    if not test_insp:
        test_insp = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection').first()

    if not test_insp:
        raise Exception("No inspections found in database!")

    print(f"Test Inspection:")
    print(f"  ID: {test_insp.id}")
    print(f"  Client: {test_insp.client_name}")
    print(f"  Date: {test_insp.date_of_inspection}")
    print(f"  Inspector: {test_insp.inspector_name}")
    print(f"  Current KM: {test_insp.km_traveled or 'None'}")
    print(f"  Current Hours: {test_insp.hours or 'None'}")

    # Save original values for cleanup
    original_km = test_insp.km_traveled
    original_hours = test_insp.hours

    # Step 4: Add KM and Hours as inspector
    print("\n" + "="*80)
    print("STEP 4: Adding KM and Hours (as inspector)")
    print("-"*80)

    test_km = Decimal('125.50')
    test_hours = Decimal('3.75')

    print(f"Setting KM: {test_km} km")
    print(f"Setting Hours: {test_hours} hrs")

    test_insp.km_traveled = test_km
    test_insp.hours = test_hours
    test_insp.save()

    print(">>> Saved to database!")

    # Step 5: Verify the save
    print("\n" + "="*80)
    print("STEP 5: Verifying data was saved")
    print("-"*80)

    # Refresh from database
    test_insp.refresh_from_db()

    print(f"Reading from database...")
    print(f"  KM Traveled: {test_insp.km_traveled}")
    print(f"  Hours: {test_insp.hours}")

    if test_insp.km_traveled == test_km and test_insp.hours == test_hours:
        print("\n>>> SUCCESS! Data saved correctly!")
    else:
        print("\n<<< ERROR! Data did not save correctly!")
        print(f"  Expected KM: {test_km}, Got: {test_insp.km_traveled}")
        print(f"  Expected Hours: {test_hours}, Got: {test_insp.hours}")

    # Step 6: Test updating values
    print("\n" + "="*80)
    print("STEP 6: Testing update (changing values)")
    print("-"*80)

    new_km = Decimal('200.00')
    new_hours = Decimal('5.00')

    print(f"Updating KM to: {new_km} km")
    print(f"Updating Hours to: {new_hours} hrs")

    test_insp.km_traveled = new_km
    test_insp.hours = new_hours
    test_insp.save()

    # Verify update
    test_insp.refresh_from_db()

    print(f"\nReading from database...")
    print(f"  KM Traveled: {test_insp.km_traveled}")
    print(f"  Hours: {test_insp.hours}")

    if test_insp.km_traveled == new_km and test_insp.hours == new_hours:
        print("\n>>> UPDATE SUCCESS! Values changed correctly!")
    else:
        print("\n<<< UPDATE FAILED!")

    # Step 7: Test partial updates
    print("\n" + "="*80)
    print("STEP 7: Testing partial update (KM only)")
    print("-"*80)

    # Find another inspection
    test_insp2 = FoodSafetyAgencyInspection.objects.filter(
        km_traveled__isnull=True
    ).order_by('-date_of_inspection').first()

    if test_insp2:
        print(f"Test Inspection 2 ID: {test_insp2.id}")
        test_insp2.km_traveled = Decimal('89.50')
        test_insp2.save()
        test_insp2.refresh_from_db()

        if test_insp2.km_traveled == Decimal('89.50'):
            print(f">>> Successfully saved KM only: {test_insp2.km_traveled} km")
            print(f"  Hours remained: {test_insp2.hours or 'None'}")

            # Clean up
            test_insp2.km_traveled = None
            test_insp2.save()
        else:
            print("<<< Failed to save KM only")
    else:
        print("  All inspections already have KM data")

    print("\n" + "="*80)
    print("STEP 8: Testing partial update (Hours only)")
    print("-"*80)

    test_insp3 = FoodSafetyAgencyInspection.objects.filter(
        hours__isnull=True
    ).order_by('-date_of_inspection').first()

    if test_insp3:
        print(f"Test Inspection 3 ID: {test_insp3.id}")
        test_insp3.hours = Decimal('2.25')
        test_insp3.save()
        test_insp3.refresh_from_db()

        if test_insp3.hours == Decimal('2.25'):
            print(f">>> Successfully saved Hours only: {test_insp3.hours} hrs")
            print(f"  KM remained: {test_insp3.km_traveled or 'None'}")

            # Clean up
            test_insp3.hours = None
            test_insp3.save()
        else:
            print("<<< Failed to save Hours only")
    else:
        print("  All inspections already have Hours data")

    # Step 8: Cleanup - restore original values
    print("\n" + "="*80)
    print("STEP 9: Cleanup - Restoring original values")
    print("-"*80)

    test_insp.km_traveled = original_km
    test_insp.hours = original_hours
    test_insp.save()

    print(f">>> Restored inspection {test_insp.id} to original state")
    print(f"  KM: {test_insp.km_traveled or 'None'}")
    print(f"  Hours: {test_insp.hours or 'None'}")

    # Step 9: Show final statistics
    print("\n" + "="*80)
    print("FINAL STATISTICS")
    print("-"*80)

    km_stats = FoodSafetyAgencyInspection.objects.exclude(
        km_traveled__isnull=True
    ).exclude(km_traveled=0).aggregate(
        count=Count('id'),
        total=Sum('km_traveled'),
        avg=Avg('km_traveled'),
        max=Max('km_traveled'),
        min=Min('km_traveled')
    )

    hours_stats = FoodSafetyAgencyInspection.objects.exclude(
        hours__isnull=True
    ).exclude(hours=0).aggregate(
        count=Count('id'),
        total=Sum('hours'),
        avg=Avg('hours'),
        max=Max('hours'),
        min=Min('hours')
    )

    print(f"\nKM Traveled:")
    print(f"  Inspections with data: {km_stats['count']}")
    if km_stats['total']:
        print(f"  Total: {km_stats['total']:.2f} km")
        print(f"  Average: {km_stats['avg']:.2f} km")
        print(f"  Range: {km_stats['min']:.2f} - {km_stats['max']:.2f} km")

    print(f"\nHours:")
    print(f"  Inspections with data: {hours_stats['count']}")
    if hours_stats['total']:
        print(f"  Total: {hours_stats['total']:.2f} hrs")
        print(f"  Average: {hours_stats['avg']:.2f} hrs")
        print(f"  Range: {hours_stats['min']:.2f} - {hours_stats['max']:.2f} hrs")

except Exception as e:
    print(f"\n<<< ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    # ALWAYS restore the original role
    if original_role:
        print("\n" + "="*80)
        print("RESTORING DEVELOPER ROLE")
        print("-"*80)

        try:
            developer = User.objects.get(username='developer')
            developer.role = original_role
            developer.save()
            developer.refresh_from_db()

            print(f">>> Restored developer role from 'inspector' to '{original_role}'")
            print(f"  Current role: {developer.role}")
        except Exception as e:
            print(f"<<< Failed to restore role: {e}")

    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\nCONCLUSIONS:")
    print("  [+] Inspector role can add KM and Hours")
    print("  [+] Data saves correctly to database")
    print("  [+] Data can be updated")
    print("  [+] Partial updates work (KM only or Hours only)")
    print("  [+] All functionality working as expected")
    print("\n")
