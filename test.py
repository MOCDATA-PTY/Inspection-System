"""
Comprehensive test script to diagnose km and hours data in the database
This will help identify where the data is and why it's not showing up
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Count, Q
from datetime import datetime, timedelta

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_section(text):
    """Print a formatted section"""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80)

def main():
    print_header("KM AND HOURS DATA DIAGNOSIS")

    # ========================================================================
    # PART 1: Check total inspections
    # ========================================================================
    print_section("PART 1: Total Inspections in Database")
    total_inspections = FoodSafetyAgencyInspection.objects.all().count()
    print(f"Total inspections in database: {total_inspections}")

    # ========================================================================
    # PART 2: Check for km_traveled field
    # ========================================================================
    print_section("PART 2: Checking km_traveled field")

    # Count inspections with km_traveled
    with_km = FoodSafetyAgencyInspection.objects.filter(
        km_traveled__isnull=False
    ).exclude(km_traveled=0).count()

    without_km = FoodSafetyAgencyInspection.objects.filter(
        Q(km_traveled__isnull=True) | Q(km_traveled=0)
    ).count()

    print(f"Inspections WITH km_traveled (not null and not 0): {with_km}")
    print(f"Inspections WITHOUT km_traveled (null or 0): {without_km}")
    print(f"Percentage with km_traveled: {(with_km/total_inspections*100) if total_inspections > 0 else 0:.2f}%")

    # Show sample records with km_traveled
    if with_km > 0:
        print("\n[FOUND] Sample inspections WITH km_traveled:")
        sample_with_km = FoodSafetyAgencyInspection.objects.filter(
            km_traveled__isnull=False
        ).exclude(km_traveled=0)[:5]

        for insp in sample_with_km:
            print(f"  - ID: {insp.id} | Commodity: {insp.commodity} | Remote ID: {insp.remote_id}")
            print(f"    Inspector: {insp.inspector_name} | Date: {insp.date_of_inspection}")
            print(f"    KM Traveled: {insp.km_traveled}")
            print(f"    Client: {insp.client_name}")
    else:
        print("\n[WARNING] NO inspections found with km_traveled data!")

    # ========================================================================
    # PART 3: Check for hours field
    # ========================================================================
    print_section("PART 3: Checking hours field")

    # Count inspections with hours
    with_hours = FoodSafetyAgencyInspection.objects.filter(
        hours__isnull=False
    ).exclude(hours=0).count()

    without_hours = FoodSafetyAgencyInspection.objects.filter(
        Q(hours__isnull=True) | Q(hours=0)
    ).count()

    print(f"Inspections WITH hours (not null and not 0): {with_hours}")
    print(f"Inspections WITHOUT hours (null or 0): {without_hours}")
    print(f"Percentage with hours: {(with_hours/total_inspections*100) if total_inspections > 0 else 0:.2f}%")

    # Show sample records with hours
    if with_hours > 0:
        print("\n[FOUND] Sample inspections WITH hours:")
        sample_with_hours = FoodSafetyAgencyInspection.objects.filter(
            hours__isnull=False
        ).exclude(hours=0)[:5]

        for insp in sample_with_hours:
            print(f"  - ID: {insp.id} | Commodity: {insp.commodity} | Remote ID: {insp.remote_id}")
            print(f"    Inspector: {insp.inspector_name} | Date: {insp.date_of_inspection}")
            print(f"    Hours: {insp.hours}")
            print(f"    Client: {insp.client_name}")
    else:
        print("\n[WARNING] NO inspections found with hours data!")

    # ========================================================================
    # PART 4: Check for inspection_travel_distance_km field (from SQL Server)
    # ========================================================================
    print_section("PART 4: Checking inspection_travel_distance_km field (from SQL Server)")

    # Count inspections with inspection_travel_distance_km
    with_sql_km = FoodSafetyAgencyInspection.objects.filter(
        inspection_travel_distance_km__isnull=False
    ).exclude(inspection_travel_distance_km=0).count()

    without_sql_km = FoodSafetyAgencyInspection.objects.filter(
        Q(inspection_travel_distance_km__isnull=True) | Q(inspection_travel_distance_km=0)
    ).count()

    print(f"Inspections WITH inspection_travel_distance_km (not null and not 0): {with_sql_km}")
    print(f"Inspections WITHOUT inspection_travel_distance_km (null or 0): {without_sql_km}")
    print(f"Percentage with inspection_travel_distance_km: {(with_sql_km/total_inspections*100) if total_inspections > 0 else 0:.2f}%")

    # Show sample records with inspection_travel_distance_km
    if with_sql_km > 0:
        print("\n[FOUND] Sample inspections WITH inspection_travel_distance_km:")
        sample_with_sql_km = FoodSafetyAgencyInspection.objects.filter(
            inspection_travel_distance_km__isnull=False
        ).exclude(inspection_travel_distance_km=0)[:5]

        for insp in sample_with_sql_km:
            print(f"  - ID: {insp.id} | Commodity: {insp.commodity} | Remote ID: {insp.remote_id}")
            print(f"    Inspector: {insp.inspector_name} | Date: {insp.date_of_inspection}")
            print(f"    Inspection Travel Distance KM: {insp.inspection_travel_distance_km}")
            print(f"    Client: {insp.client_name}")
    else:
        print("\n[WARNING] NO inspections found with inspection_travel_distance_km data!")

    # ========================================================================
    # PART 5: Check by commodity
    # ========================================================================
    print_section("PART 5: Breakdown by Commodity")

    commodities = FoodSafetyAgencyInspection.objects.values('commodity').distinct()

    for commodity_dict in commodities:
        commodity = commodity_dict['commodity']
        if not commodity:
            continue

        total = FoodSafetyAgencyInspection.objects.filter(commodity=commodity).count()
        with_km = FoodSafetyAgencyInspection.objects.filter(
            commodity=commodity,
            km_traveled__isnull=False
        ).exclude(km_traveled=0).count()

        with_hours = FoodSafetyAgencyInspection.objects.filter(
            commodity=commodity,
            hours__isnull=False
        ).exclude(hours=0).count()

        with_sql_km = FoodSafetyAgencyInspection.objects.filter(
            commodity=commodity,
            inspection_travel_distance_km__isnull=False
        ).exclude(inspection_travel_distance_km=0).count()

        print(f"\n{commodity}:")
        print(f"  Total: {total}")
        print(f"  With km_traveled: {with_km} ({(with_km/total*100) if total > 0 else 0:.1f}%)")
        print(f"  With hours: {with_hours} ({(with_hours/total*100) if total > 0 else 0:.1f}%)")
        print(f"  With inspection_travel_distance_km: {with_sql_km} ({(with_sql_km/total*100) if total > 0 else 0:.1f}%)")

    # ========================================================================
    # PART 6: Check recent inspections
    # ========================================================================
    print_section("PART 6: Recent Inspections (last 30 days)")

    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=thirty_days_ago
    )

    recent_count = recent_inspections.count()
    print(f"Total recent inspections: {recent_count}")

    if recent_count > 0:
        recent_with_km = recent_inspections.filter(
            km_traveled__isnull=False
        ).exclude(km_traveled=0).count()

        recent_with_hours = recent_inspections.filter(
            hours__isnull=False
        ).exclude(hours=0).count()

        print(f"Recent with km_traveled: {recent_with_km} ({(recent_with_km/recent_count*100) if recent_count > 0 else 0:.1f}%)")
        print(f"Recent with hours: {recent_with_hours} ({(recent_with_hours/recent_count*100) if recent_count > 0 else 0:.1f}%)")

        # Show 5 most recent
        print("\n[RECENT] 5 Most Recent Inspections:")
        recent_sample = recent_inspections.order_by('-date_of_inspection')[:5]
        for insp in recent_sample:
            print(f"  - ID: {insp.id} | Date: {insp.date_of_inspection} | {insp.commodity}")
            print(f"    Inspector: {insp.inspector_name}")
            print(f"    Client: {insp.client_name}")
            print(f"    km_traveled: {insp.km_traveled or 'NULL'}")
            print(f"    hours: {insp.hours or 'NULL'}")
            print(f"    inspection_travel_distance_km: {insp.inspection_travel_distance_km or 'NULL'}")

    # ========================================================================
    # PART 7: Summary and Recommendations
    # ========================================================================
    print_section("SUMMARY AND RECOMMENDATIONS")

    print("\n[SUMMARY] Field Usage Summary:")
    print(f"  - km_traveled: {with_km}/{total_inspections} ({(with_km/total_inspections*100) if total_inspections > 0 else 0:.1f}%)")
    print(f"  - hours: {with_hours}/{total_inspections} ({(with_hours/total_inspections*100) if total_inspections > 0 else 0:.1f}%)")
    print(f"  - inspection_travel_distance_km: {with_sql_km}/{total_inspections} ({(with_sql_km/total_inspections*100) if total_inspections > 0 else 0:.1f}%)")

    print("\n[RECOMMENDATIONS]")
    if with_km == 0 and with_hours == 0:
        print("  [WARNING] ISSUE: No km_traveled or hours data found!")
        print("  --> These fields are for manual entry by inspectors")
        print("  --> Check if the frontend forms are correctly submitting to save-km-hours endpoint")
        print("  --> Check if the save_group_km_hours view is working properly")
        print("  --> Verify JavaScript functions updateGroupKmTraveled() and updateGroupHours() are working")
    elif with_km > 0 or with_hours > 0:
        print("  [OK] Some manual km/hours data exists")
        print("  --> Check template files to ensure fields are displaying correctly")
        print("  --> Verify JavaScript functions updateGroupKmTraveled() and updateGroupHours() are working")

    if with_sql_km > 0:
        print(f"  [INFO] inspection_travel_distance_km has data from SQL Server ({with_sql_km} records)")
        print("  --> This is automatically synced from the RAW commodity table")
        print("  --> Only RAW commodity has this field in SQL Server")

    print("\n[NEXT STEPS] Where to look:")
    print("  1. Check export_sheet.html template for the input fields")
    print("  2. Check core_views.py for the save_group_km_hours endpoint")
    print("  3. Check JavaScript console for any errors when entering km/hours")
    print("  4. Verify the CSRF token is being passed correctly")

    print("\n[COMPLETE] Diagnosis complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()
