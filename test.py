"""
COMPREHENSIVE TEST - Test compliance status detection and sent status functionality
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

def run_comprehensive_test():
    """Run comprehensive test of compliance status and sent functionality"""

    print("="*100)
    print(" " * 35 + "COMPREHENSIVE TEST")
    print("="*100)

    client_name = "Hume International"
    inspection_date = date(2025, 10, 17)

    # TEST 1: Find inspections
    print("\n" + "="*100)
    print("TEST 1: FIND INSPECTIONS")
    print("="*100)

    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains=client_name,
        date_of_inspection=inspection_date
    )

    print(f"\nSearching for: {client_name} on {inspection_date}")
    print(f"Found: {inspections.count()} inspection(s)")

    if inspections.count() == 0:
        print("❌ TEST 1 FAILED - No inspections found")
        return False

    for insp in inspections:
        print(f"\n  Inspection ID: {insp.id}")
        print(f"  Remote ID: {insp.remote_id}")
        print(f"  Client: {insp.client_name}")
        print(f"  Date: {insp.date_of_inspection}")
        print(f"  Commodity: {insp.commodity}")
        print(f"  RFI uploaded: {insp.rfi_uploaded_date}")
        print(f"  Invoice uploaded: {insp.invoice_uploaded_date}")
        print(f"  is_direction_present: {insp.is_direction_present_for_this_inspection}")
        print(f"  is_sent: {insp.is_sent}")
        print(f"  sent_date: {insp.sent_date}")

    print("\n✅ TEST 1 PASSED")

    # TEST 2: Check for files in uploads folder
    print("\n" + "="*100)
    print("TEST 2: CHECK FILES IN UPLOADS FOLDER")
    print("="*100)

    uploads_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'inspections')
    print(f"\nChecking: {uploads_path}")

    if not os.path.exists(uploads_path):
        print(f"❌ TEST 2 FAILED - Uploads folder does not exist: {uploads_path}")
        return False

    print(f"✅ Folder exists")

    files = os.listdir(uploads_path)
    print(f"\nTotal files in folder: {len(files)}")

    # Look for Hume International files
    client_sanitized = "hume_international"
    date_str = "20251017"

    rfi_files = [f for f in files if 'rfi' in f.lower() and client_sanitized in f.lower() and date_str in f]
    invoice_files = [f for f in files if 'invoice' in f.lower() and client_sanitized in f.lower() and date_str in f]
    compliance_files = [f for f in files if 'compliance' in f.lower() and client_sanitized in f.lower() and date_str in f]

    print(f"\nRFI files found: {len(rfi_files)}")
    for f in rfi_files:
        print(f"  - {f}")

    print(f"\nInvoice files found: {len(invoice_files)}")
    for f in invoice_files:
        print(f"  - {f}")

    print(f"\nCompliance files found: {len(compliance_files)}")
    for f in compliance_files:
        print(f"  - {f}")

    if len(rfi_files) == 0 or len(invoice_files) == 0 or len(compliance_files) == 0:
        print("\n❌ TEST 2 FAILED - Missing files!")
        if len(rfi_files) == 0:
            print("  Missing: RFI file")
        if len(invoice_files) == 0:
            print("  Missing: Invoice file")
        if len(compliance_files) == 0:
            print("  Missing: Compliance file")
        return False

    print("\n✅ TEST 2 PASSED - All files present")

    # TEST 3: Test compliance status check function
    print("\n" + "="*100)
    print("TEST 3: TEST COMPLIANCE STATUS CHECK FUNCTION")
    print("="*100)

    try:
        from main.views.core_views import check_compliance_documents_status

        print(f"\nTesting: check_compliance_documents_status()")
        print(f"Client: {client_name}")
        print(f"Date: {inspection_date}")
        print(f"Inspections: {inspections.count()}")

        result = check_compliance_documents_status(
            inspections,
            client_name,
            inspection_date
        )

        print(f"\nResult:")
        print(f"  has_any_compliance: {result.get('has_any_compliance', False)}")
        print(f"  all_commodities_have_compliance: {result.get('all_commodities_have_compliance', False)}")
        print(f"  commodity_status: {result.get('commodity_status', {})}")

        if result.get('has_any_compliance', False):
            print("\n✅ TEST 3 PASSED - Compliance detected")
        else:
            print("\n❌ TEST 3 FAILED - Compliance NOT detected")
            print("\n  This is the BUG! Files exist but function doesn't detect them.")
            return False

    except Exception as e:
        print(f"\n❌ TEST 3 FAILED - Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    # TEST 4: Calculate compliance_status (like the view does)
    print("\n" + "="*100)
    print("TEST 4: CALCULATE COMPLIANCE_STATUS (LIKE SHIPMENT LIST VIEW)")
    print("="*100)

    has_rfi = inspections.first().rfi_uploaded_date is not None
    has_invoice = inspections.first().invoice_uploaded_date is not None
    has_compliance = result.get('has_any_compliance', False)

    print(f"\nFile checks:")
    print(f"  has_rfi: {has_rfi}")
    print(f"  has_invoice: {has_invoice}")
    print(f"  has_compliance: {has_compliance}")

    if has_rfi and has_invoice and has_compliance:
        compliance_status = 'complete'
    elif has_rfi or has_invoice or has_compliance:
        compliance_status = 'partial'
    else:
        compliance_status = 'no_compliance'

    print(f"\nCalculated compliance_status: {compliance_status}")

    if compliance_status == 'complete':
        print("✅ Sent dropdown SHOULD BE ENABLED")
        print("\n✅ TEST 4 PASSED")
    else:
        print("❌ Sent dropdown WILL BE DISABLED")
        print(f"\n❌ TEST 4 FAILED - compliance_status is '{compliance_status}' instead of 'complete'")
        return False

    # TEST 5: Check current sent status
    print("\n" + "="*100)
    print("TEST 5: CHECK CURRENT SENT STATUS IN DATABASE")
    print("="*100)

    inspection = inspections.first()
    print(f"\nInspection {inspection.id}:")
    print(f"  is_sent: {inspection.is_sent}")
    print(f"  sent_by: {inspection.sent_by}")
    print(f"  sent_date: {inspection.sent_date}")

    if inspection.is_sent:
        print("\n✅ TEST 5 PASSED - Inspection is marked as SENT")
    else:
        print("\n❌ TEST 5 FAILED - Inspection is NOT marked as sent")
        print("   Run mark_as_sent.py to mark it as sent")
        return False

    # FINAL SUMMARY
    print("\n" + "="*100)
    print(" " * 40 + "FINAL SUMMARY")
    print("="*100)

    print("\n✅ ALL TESTS PASSED!")
    print("\n  1. ✅ Inspections found in database")
    print("  2. ✅ All files present in uploads folder")
    print("  3. ✅ Compliance status function detects files")
    print("  4. ✅ compliance_status = 'complete'")
    print("  5. ✅ Inspection marked as sent in database")

    print("\n" + "="*100)
    print("CONCLUSION: System is working correctly!")
    print("="*100)
    print("\nIf the browser still shows 'Not Sent':")
    print("  1. Clear ALL browser cache (Ctrl+Shift+Del)")
    print("  2. Close ALL browser tabs")
    print("  3. Restart the browser")
    print("  4. Navigate to the page again")
    print("\nThe page should now show 'Sent' status with timestamp!")

    return True


if __name__ == '__main__':
    print("\n" + "="*100)
    print(" " * 30 + "STARTING COMPREHENSIVE TEST")
    print("="*100)

    try:
        success = run_comprehensive_test()

        if success:
            print("\n\n" + "="*100)
            print(" " * 35 + "✅ ALL TESTS PASSED ✅")
            print("="*100)
            sys.exit(0)
        else:
            print("\n\n" + "="*100)
            print(" " * 35 + "❌ SOME TESTS FAILED ❌")
            print("="*100)
            sys.exit(1)

    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
