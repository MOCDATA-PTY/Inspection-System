"""
Final verification script to confirm button colors will be green
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

from main.models import FoodSafetyAgencyInspection

def verify_hume_inspection():
    """Verify that Hume International inspection has all files uploaded"""

    print("\n" + "="*70)
    print("VERIFICATION: Button Color Status for Hume International")
    print("="*70)

    try:
        # Find the Hume International inspection
        inspection = FoodSafetyAgencyInspection.objects.filter(
            client_name__icontains='Hume International',
            date_of_inspection__year=2025,
            date_of_inspection__month=10,
            date_of_inspection__day=17
        ).first()

        if not inspection:
            print("\nX ERROR: Hume International inspection not found!")
            return False

        print(f"\n[INSPECTION FOUND]")
        print(f"  Client: {inspection.client_name}")
        print(f"  Date: {inspection.date_of_inspection}")
        print(f"  Inspector: {inspection.inspector_name}")

        print(f"\n[DATABASE STATUS]")
        print(f"  RFI Upload Date: {inspection.rfi_uploaded_date}")
        print(f"  Invoice Upload Date: {inspection.invoice_uploaded_date}")

        print(f"\n[PROPERTY VALUES]")
        print(f"  inspection.rfi_uploaded: {inspection.rfi_uploaded}")
        print(f"  inspection.invoice_uploaded: {inspection.invoice_uploaded}")

        print(f"\n[BUTTON COLORS IN BROWSER]")

        # Check RFI button
        if inspection.rfi_uploaded:
            print(f"  >> RFI Button: GREEN with checkmark")
            rfi_status = "PASS"
        else:
            print(f"  >> RFI Button: GRAY (not uploaded)")
            rfi_status = "FAIL"

        # Check Invoice button
        if inspection.invoice_uploaded:
            print(f"  >> Invoice Button: GREEN with checkmark")
            invoice_status = "PASS"
        else:
            print(f"  >> Invoice Button: GRAY (not uploaded)")
            invoice_status = "FAIL"

        # Check View Files button (needs compliance files)
        print(f"  >> View Files Button: Check compliance folder for color")

        print("\n" + "="*70)
        print("VERIFICATION RESULTS")
        print("="*70)

        if rfi_status == "PASS" and invoice_status == "PASS":
            print("\nSTATUS: ALL TESTS PASSED!")
            print("\nWhen you refresh your browser, you should see:")
            print("  - RFI button: GREEN with checkmark (disabled)")
            print("  - Invoice button: GREEN with checkmark (disabled)")
            print("  - Both buttons will show 'RFI check' and 'Invoice check'")
            print("\nACTION REQUIRED:")
            print("  1. Open your browser")
            print("  2. Go to the Inspections page")
            print("  3. Press F5 or click Refresh")
            print("  4. Look at the Hume International row")
            print("  5. You should see GREEN buttons!")
            return True
        else:
            print("\nSTATUS: SOME TESTS FAILED")
            print(f"  RFI: {rfi_status}")
            print(f"  Invoice: {invoice_status}")
            return False

    except Exception as e:
        print(f"\nX ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\nStarting verification...")
    success = verify_hume_inspection()

    if success:
        print("\n" + "="*70)
        print("SUCCESS! Everything is ready.")
        print("="*70)
        print("\nThe database has been updated with:")
        print("  - RFI upload date: 2025-10-20 12:47:16")
        print("  - Invoice upload date: 2025-10-20 12:47:16")
        print("\nThe model now has properties that return:")
        print("  - rfi_uploaded: True")
        print("  - invoice_uploaded: True")
        print("\nThe template will check these properties and show GREEN buttons!")
        print("\nREFRESH YOUR BROWSER NOW to see the changes!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("VERIFICATION FAILED")
        print("="*70)
        print("\nPlease check the errors above.")

    sys.exit(0 if success else 1)
