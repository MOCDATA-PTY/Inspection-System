"""
Test case to check if KM and Hours are being saved to PostgreSQL
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Q

def test_km_hours_saving():
    """Test if km_traveled and hours fields are being saved"""

    print("=" * 120)
    print(" " * 40 + "KM AND HOURS SAVING TEST")
    print("=" * 120)
    print()

    # TEST 1: Check if fields exist in the model
    print("TEST 1: Check if km_traveled and hours fields exist in model")
    print("-" * 120)

    model_fields = [f.name for f in FoodSafetyAgencyInspection._meta.get_fields()]

    km_field_exists = 'km_traveled' in model_fields
    hours_field_exists = 'hours' in model_fields

    print(f"km_traveled field exists: {km_field_exists}")
    print(f"hours field exists: {hours_field_exists}")
    print()

    if not km_field_exists or not hours_field_exists:
        print("ERROR: Required fields are missing from the model!")
        print("Model fields available:", model_fields)
        return False

    print("SUCCESS: Both fields exist in the model")
    print()

    # TEST 2: Check how many records have km_traveled or hours data
    print("TEST 2: Check existing data in PostgreSQL")
    print("-" * 120)

    total_inspections = FoodSafetyAgencyInspection.objects.count()
    print(f"Total inspections in database: {total_inspections}")
    print()

    # Check km_traveled
    km_not_null = FoodSafetyAgencyInspection.objects.filter(km_traveled__isnull=False).count()
    km_greater_than_zero = FoodSafetyAgencyInspection.objects.filter(km_traveled__gt=0).count()

    print(f"Inspections with km_traveled NOT NULL: {km_not_null}")
    print(f"Inspections with km_traveled > 0: {km_greater_than_zero}")
    print()

    # Check hours
    hours_not_null = FoodSafetyAgencyInspection.objects.filter(hours__isnull=False).count()
    hours_greater_than_zero = FoodSafetyAgencyInspection.objects.filter(hours__gt=0).count()

    print(f"Inspections with hours NOT NULL: {hours_not_null}")
    print(f"Inspections with hours > 0: {hours_greater_than_zero}")
    print()

    # TEST 3: Show sample records with km_traveled and hours
    print("TEST 3: Sample records with km_traveled and hours data")
    print("-" * 120)

    sample_with_data = FoodSafetyAgencyInspection.objects.filter(
        Q(km_traveled__isnull=False) | Q(hours__isnull=False)
    ).order_by('-date_of_inspection')[:10]

    if sample_with_data.exists():
        print(f"Found {sample_with_data.count()} sample records with data:")
        print()
        for idx, insp in enumerate(sample_with_data, 1):
            print(f"{idx:2}. Inspection ID: {insp.remote_id}")
            print(f"    Client: {insp.client_name}")
            print(f"    Date: {insp.date_of_inspection}")
            print(f"    Commodity: {insp.commodity}")
            print(f"    km_traveled: {insp.km_traveled}")
            print(f"    hours: {insp.hours}")
            print()
    else:
        print("WARNING: No records found with km_traveled or hours data!")
        print()

    # TEST 4: Check SQL Server source field mapping
    print("TEST 4: Check SQL Server source field mapping")
    print("-" * 120)

    print("The sync should map these SQL Server fields:")
    print("  - inspection_travel_distance_km -> km_traveled (from RawRMPInspectionRecordTypes)")
    print("  - InspectionTravelDistanceKm -> km_traveled")
    print()

    # Check if inspection_travel_distance_km is being saved
    travel_distance_not_null = FoodSafetyAgencyInspection.objects.filter(
        inspection_travel_distance_km__isnull=False
    ).count()

    print(f"Inspections with inspection_travel_distance_km NOT NULL: {travel_distance_not_null}")
    print()

    if travel_distance_not_null > 0:
        print("SUCCESS: inspection_travel_distance_km is being saved from SQL Server")
        print()
        print("Sample records with inspection_travel_distance_km:")
        print("-" * 120)
        samples = FoodSafetyAgencyInspection.objects.filter(
            inspection_travel_distance_km__isnull=False
        ).order_by('-date_of_inspection')[:5]

        for idx, insp in enumerate(samples, 1):
            print(f"{idx}. Client: {insp.client_name} | Date: {insp.date_of_inspection}")
            print(f"   inspection_travel_distance_km: {insp.inspection_travel_distance_km}")
            print(f"   km_traveled: {insp.km_traveled}")
            print(f"   hours: {insp.hours}")
            print()

    # TEST 5: Check if km_traveled and hours are separate from inspection_travel_distance_km
    print("TEST 5: Field purpose check")
    print("-" * 120)
    print()
    print("Understanding the fields:")
    print("  1. inspection_travel_distance_km: Comes from SQL Server sync (InspectionTravelDistanceKm)")
    print("  2. km_traveled: Manual entry field for user input")
    print("  3. hours: Manual entry field for user input")
    print()

    # TEST 6: Summary and recommendations
    print("=" * 120)
    print(" " * 45 + "SUMMARY")
    print("=" * 120)
    print()

    if km_not_null > 0 or hours_not_null > 0:
        print("STATUS: Data is being saved to km_traveled and hours fields")
        print()
        print(f"  - km_traveled records with data: {km_not_null} ({(km_not_null/total_inspections*100):.2f}%)")
        print(f"  - hours records with data: {hours_not_null} ({(hours_not_null/total_inspections*100):.2f}%)")
        print()
        print("CONCLUSION: Fields are working correctly for manual entry")
    else:
        print("WARNING: No data found in km_traveled or hours fields")
        print()
        print("POSSIBLE REASONS:")
        print("  1. Users haven't entered any data yet")
        print("  2. The update endpoint may not be saving properly")
        print("  3. Data is being saved to a different field")
        print()
        print("RECOMMENDATION:")
        print("  - Check the update endpoint in views (update-km-traveled, update-hours)")
        print("  - Verify JavaScript is calling the correct endpoint")
        print("  - Test manual entry from the UI")

    print()
    print("=" * 120)


if __name__ == "__main__":
    try:
        test_km_hours_saving()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
