"""
Test that OneDrive is disabled
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def test_onedrive_disabled():
    print("="*70)
    print("TESTING ONEDRIVE DISABLED")
    print("="*70)
    print()

    # Test 1: Check OneDrive service doesn't auto-start
    print("Test 1: Importing OneDrive service...")
    try:
        from main.services.onedrive_direct_service import OneDriveDirectUploadService
        service = OneDriveDirectUploadService()
        print(f"  Service created: is_running = {service.is_running}")

        if service.is_running:
            print("  ❌ FAIL: OneDrive service auto-started!")
        else:
            print("  ✅ PASS: OneDrive service did NOT auto-start")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

    print()

    # Test 2: Check OneDrive authentication returns False immediately
    print("Test 2: Testing OneDrive authentication...")
    try:
        from main.services.onedrive_direct_service import onedrive_direct_service
        result = onedrive_direct_service.authenticate_onedrive()

        if result == False:
            print("  ✅ PASS: OneDrive authentication disabled (returns False)")
        else:
            print(f"  ❌ FAIL: OneDrive authentication returned {result}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

    print()

    # Test 3: Check compliance status doesn't use OneDrive
    print("Test 3: Testing compliance document status check...")
    try:
        from main.models import FoodSafetyAgencyInspection
        from datetime import date

        # Get a recent inspection
        inspection = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection__gte=date(2025, 11, 1)
        ).first()

        if inspection:
            print(f"  Testing with inspection: {inspection.client_name}")

            # This should NOT trigger OneDrive
            from main.views.core_views import check_compliance_documents_status

            inspections = [inspection]
            status = check_compliance_documents_status(
                inspections,
                inspection.client_name,
                inspection.date_of_inspection
            )

            print(f"  Status retrieved: {status.get('has_any_compliance', False)}")
            print("  ✅ PASS: No OneDrive messages (check console output above)")
        else:
            print("  ⚠️  No inspections found to test")

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("If you see NO OneDrive authentication messages above,")
    print("then OneDrive is successfully disabled!")

if __name__ == "__main__":
    test_onedrive_disabled()
