import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from main.views.core_views import check_compliance_documents_status
from datetime import datetime
from django.core.cache import cache

# Clear cache to get fresh results
print("Clearing cache...")
cache.clear()
print("Cache cleared.\n")

# Find the inspection for Hume International
# with inspection date 17/10/2025
try:
    # Convert the date string to a date object
    inspection_date = datetime.strptime('17/10/2025', '%d/%m/%Y').date()

    # Find all inspections for Hume International on that date
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains='Hume',
        date_of_inspection=inspection_date
    )

    if not inspections:
        print("No inspections found for Hume International on 17/10/2025")
    else:
        print(f"Found {inspections.count()} inspection(s):")
        for inspection in inspections:
            print(f"\n  Client: {inspection.client_name}")
            print(f"  Inspector: {inspection.inspector_name}")
            print(f"  Inspection Date: {inspection.date_of_inspection}")
            print(f"  Commodity: {inspection.commodity}")
            print(f"  RFI uploaded: {inspection.rfi_uploaded}")
            print(f"  Invoice uploaded: {inspection.invoice_uploaded}")

        # Check compliance documents status
        print(f"\nChecking compliance documents status...")
        client_name = inspections[0].client_name
        date_of_inspection = inspections[0].date_of_inspection

        compliance_result = check_compliance_documents_status(inspections, client_name, date_of_inspection)

        print(f"\nCompliance Status Result:")
        print(f"  has_any_compliance: {compliance_result.get('has_any_compliance')}")
        print(f"  all_commodities_have_compliance: {compliance_result.get('all_commodities_have_compliance')}")
        print(f"  commodity_status: {compliance_result.get('commodity_status')}")

        # Calculate what the compliance_status would be
        has_rfi = inspections[0].rfi_uploaded
        has_invoice = inspections[0].invoice_uploaded
        has_compliance = compliance_result.get('has_any_compliance', False)

        print(f"\nFile Upload Status:")
        print(f"  has_rfi: {has_rfi}")
        print(f"  has_invoice: {has_invoice}")
        print(f"  has_compliance: {has_compliance}")

        # Determine compliance status (same logic as in view)
        if has_rfi and has_invoice and has_compliance:
            compliance_status = 'complete'
        elif has_rfi or has_invoice or has_compliance:
            compliance_status = 'partial'
        else:
            compliance_status = 'no_compliance'

        print(f"\nCalculated compliance_status: {compliance_status}")
        print(f"\nSent dropdown should be: {'Enabled' if compliance_status == 'complete' else 'DISABLED'}")

        if compliance_status != 'complete':
            print(f"\n[WARNING] Sent status cannot be changed because compliance_status is '{compliance_status}'")
            print(f"   To fix this, ensure:")
            if not has_rfi:
                print(f"     - RFI document is uploaded")
            if not has_invoice:
                print(f"     - Invoice document is uploaded")
            if not has_compliance:
                print(f"     - Compliance documents are uploaded to OneDrive")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
