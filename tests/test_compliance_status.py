"""
Comprehensive test script to diagnose the Hume International compliance status issue
"""

import os
import sys
import io
import django
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# Import after Django setup
from django.core.cache import cache
from main.models import FoodSafetyAgencyInspection
from datetime import datetime, date
from django.conf import settings

def test_compliance_status():
    """Test compliance status detection for Hume International"""

    print("="*80)
    print("COMPLIANCE STATUS DIAGNOSTIC TEST")
    print("="*80)

    # 1. Find the inspection
    print("\n[STEP 1] Finding Hume International inspection...")
    inspection = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains='Hume International',
        date_of_inspection=date(2025, 10, 17)
    ).first()

    if not inspection:
        print("   ❌ Hume International inspection not found!")
        return False

    print(f"   ✅ Found inspection:")
    print(f"      ID: {inspection.id}")
    print(f"      Remote ID: {inspection.remote_id}")
    print(f"      Client: {inspection.client_name}")
    print(f"      Date: {inspection.date_of_inspection}")
    print(f"      Inspector: {inspection.inspector_name}")
    print(f"      RFI uploaded: {inspection.rfi_uploaded_date}")
    print(f"      Invoice uploaded: {inspection.invoice_uploaded_date}")
    print(f"      is_direction_present: {inspection.is_direction_present_for_this_inspection}")

    # 2. Check for compliance files in OneDrive
    print("\n[STEP 2] Checking for compliance files in OneDrive...")

    year_folder = "2025"
    month_folder = "October"
    client_name = inspection.client_name

    # Try to import the check function from views
    try:
        from main.views.core_views import check_compliance_documents_status_onedrive

        inspections = [inspection]
        onedrive_result = check_compliance_documents_status_onedrive(
            inspections,
            client_name,
            inspection.date_of_inspection
        )

        print(f"   OneDrive check result: {onedrive_result}")

        if onedrive_result:
            print(f"   ✅ OneDrive check completed")
            print(f"      has_any_compliance: {onedrive_result.get('has_any_compliance', False)}")
            print(f"      all_commodities_have_compliance: {onedrive_result.get('all_commodities_have_compliance', False)}")
        else:
            print(f"   ⚠️  OneDrive check returned None (may not be configured)")

    except Exception as e:
        print(f"   ❌ OneDrive check failed: {e}")
        import traceback
        traceback.print_exc()

    # 3. Check for compliance files locally
    print("\n[STEP 3] Checking for compliance files in local media folder...")

    # Build all possible paths
    media_root = settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else os.path.join(BASE_DIR, 'media')

    possible_paths = [
        # Original folder structure
        os.path.join(media_root, 'inspections', year_folder, month_folder, client_name),
        # Sanitized client name
        os.path.join(media_root, 'inspections', year_folder, month_folder, 'Hume_International'),
        os.path.join(media_root, 'inspections', year_folder, month_folder, 'hume_international'),
        # Without spaces
        os.path.join(media_root, 'inspections', year_folder, month_folder, 'HumeInternational'),
        # Uploads folder
        os.path.join(media_root, 'uploads', 'inspections'),
    ]

    print(f"   Checking {len(possible_paths)} possible locations...")

    compliance_files_found = []

    for path in possible_paths:
        print(f"\n   Checking: {path}")
        if os.path.exists(path):
            print(f"      ✅ Folder exists")
            files = os.listdir(path)
            print(f"      Files in folder ({len(files)}):")
            for file in files:
                print(f"         - {file}")
                if 'compliance' in file.lower() or 'COMPLIANCE' in file:
                    compliance_files_found.append(os.path.join(path, file))
        else:
            print(f"      ❌ Folder does not exist")

    if compliance_files_found:
        print(f"\n   ✅ Found {len(compliance_files_found)} compliance file(s):")
        for f in compliance_files_found:
            print(f"      - {f}")
    else:
        print(f"\n   ❌ No compliance files found in any location")

    # 4. Test the actual compliance status check function
    print("\n[STEP 4] Testing compliance status check function...")

    try:
        from main.views.core_views import check_compliance_documents_status

        inspections_list = FoodSafetyAgencyInspection.objects.filter(
            client_name=client_name,
            date_of_inspection=inspection.date_of_inspection
        )

        print(f"   Found {inspections_list.count()} inspection(s) in group")

        compliance_result = check_compliance_documents_status(
            inspections_list,
            client_name,
            inspection.date_of_inspection
        )

        print(f"\n   Compliance status result:")
        print(f"      has_any_compliance: {compliance_result.get('has_any_compliance', False)}")
        print(f"      all_commodities_have_compliance: {compliance_result.get('all_commodities_have_compliance', False)}")
        print(f"      commodity_status: {compliance_result.get('commodity_status', {})}")

    except Exception as e:
        print(f"   ❌ Compliance status check failed: {e}")
        import traceback
        traceback.print_exc()

    # 5. Check cache status
    print("\n[STEP 5] Checking cache status...")

    cache_keys = [
        f"compliance_status_{client_name}_{inspection.date_of_inspection}",
        f"onedrive_compliance_{client_name}_{inspection.date_of_inspection}",
        f"local_compliance_{client_name}_{inspection.date_of_inspection}"
    ]

    for key in cache_keys:
        value = cache.get(key)
        if value is not None:
            print(f"   ⚠️  CACHED: {key}")
            print(f"      Value: {value}")
        else:
            print(f"   ✅ NOT CACHED: {key}")

    # 6. Simulate the shipment list view logic
    print("\n[STEP 6] Simulating shipment list view logic...")

    has_rfi = inspection.rfi_uploaded_date is not None
    has_invoice = inspection.invoice_uploaded_date is not None
    has_compliance = compliance_result.get('has_any_compliance', False) if 'compliance_result' in locals() else False

    print(f"   File status:")
    print(f"      RFI: {has_rfi}")
    print(f"      Invoice: {has_invoice}")
    print(f"      Compliance: {has_compliance}")

    if has_rfi and has_invoice and has_compliance:
        compliance_status = 'complete'
    elif has_rfi or has_invoice or has_compliance:
        compliance_status = 'partial'
    else:
        compliance_status = 'no_compliance'

    print(f"\n   Calculated compliance_status: {compliance_status}")
    print(f"   Sent dropdown should be: {'ENABLED ✅' if compliance_status == 'complete' else 'DISABLED ❌'}")

    # 7. Final diagnosis
    print("\n" + "="*80)
    print("DIAGNOSIS")
    print("="*80)

    if compliance_status == 'complete':
        print("✅ ALL CHECKS PASSED - The dropdown SHOULD be enabled")
        print("   If it's still disabled in the browser, try:")
        print("   1. Hard refresh (Ctrl+F5)")
        print("   2. Clear browser cache completely")
        print("   3. Check browser console for JavaScript errors")
    else:
        print("❌ ISSUE FOUND - The dropdown will be DISABLED")
        print(f"\n   Problem: compliance_status = '{compliance_status}'")
        print("\n   Missing files:")
        if not has_rfi:
            print("      ❌ RFI document")
        if not has_invoice:
            print("      ❌ Invoice document")
        if not has_compliance:
            print("      ❌ Compliance documents")

        print("\n   SOLUTION:")
        if not has_compliance:
            print("      The compliance documents are not being detected.")
            print("      This could be because:")
            print("      1. Files are in the wrong location")
            print("      2. Files have the wrong naming convention")
            print("      3. OneDrive check is failing")
            print("      4. Local file check is failing")

    return True


if __name__ == '__main__':
    print("\n🔍 Starting comprehensive compliance status test...\n")

    success = test_compliance_status()

    if success:
        print("\n✅ Test completed!")
    else:
        print("\n❌ Test failed!")

    sys.exit(0 if success else 1)
