"""
Test manually saving km_traveled and hours to verify the database is working
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

def test_manual_save():
    """Manually save km_traveled and hours to test if database accepts it"""

    print("=" * 100)
    print(" " * 30 + "MANUAL KM/HOURS SAVE TEST")
    print("=" * 100)
    print()

    # Get a test inspection
    inspection = FoodSafetyAgencyInspection.objects.first()

    if not inspection:
        print("ERROR: No inspections found in database")
        return False

    print(f"Test Inspection:")
    print(f"  ID: {inspection.id}")
    print(f"  Remote ID: {inspection.remote_id}")
    print(f"  Client: {inspection.client_name}")
    print(f"  Date: {inspection.date_of_inspection}")
    print()

    print("BEFORE UPDATE:")
    print(f"  km_traveled: {inspection.km_traveled}")
    print(f"  hours: {inspection.hours}")
    print()

    # Try to save km_traveled and hours
    print("Attempting to save km_traveled = 150.5 and hours = 8.5...")

    try:
        inspection.km_traveled = 150.5
        inspection.hours = 8.5
        inspection.save()

        print("SUCCESS: Data saved to database")
        print()

        # Refresh from database to confirm
        inspection.refresh_from_db()

        print("AFTER UPDATE (refreshed from database):")
        print(f"  km_traveled: {inspection.km_traveled}")
        print(f"  hours: {inspection.hours}")
        print()

        if inspection.km_traveled == 150.5 and inspection.hours == 8.5:
            print("VERIFICATION: Data correctly saved and retrieved from database!")
            print()
            print("=" * 100)
            print("CONCLUSION: The database fields are working correctly!")
            print("=" * 100)
            print()
            print("This means:")
            print("  1. The model fields are correct")
            print("  2. The database can store the data")
            print("  3. The issue is likely in the JavaScript/frontend calling the endpoint")
            print()
            print("NEXT STEPS:")
            print("  - Check JavaScript console for errors")
            print("  - Verify the input fields have correct data-inspection-id attribute")
            print("  - Check if JavaScript is calling /update-km-traveled/ endpoint")
            print("  - Verify CSRF token is being sent")
            print()

            # Clean up test data
            inspection.km_traveled = None
            inspection.hours = None
            inspection.save()
            print("Test data cleaned up (set back to None)")

            return True
        else:
            print("ERROR: Data was not saved correctly!")
            return False

    except Exception as e:
        print(f"ERROR: Failed to save: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        test_manual_save()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
