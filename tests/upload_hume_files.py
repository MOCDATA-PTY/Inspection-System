"""
Script to upload RFI, Invoice, and all required files for Hume International inspection
This will trigger the color changes in the browser
"""

import os
import sys
import io
import django
from pathlib import Path
from datetime import datetime

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

# Import Django models after setup
from main.models import FoodSafetyAgencyInspection
from django.core.files.base import ContentFile
from django.db import connection
from django.core.cache import cache


def create_fake_pdf(filename):
    """Create a minimal fake PDF file for testing"""
    fake_pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
180
%%EOF
"""
    return fake_pdf_content


def upload_files_for_hume():
    """Upload RFI, Invoice, and compliance files for Hume International"""

    print("="*60)
    print("UPLOADING FILES FOR HUME INTERNATIONAL")
    print("="*60)

    try:
        # Find the Hume International inspection
        print("\n1. Searching for Hume International inspection...")

        inspection = FoodSafetyAgencyInspection.objects.filter(
            client_name__icontains='Hume International',
            date_of_inspection__year=2025,
            date_of_inspection__month=10,
            date_of_inspection__day=17
        ).first()

        if not inspection:
            print("   ❌ Hume International inspection not found!")
            print("   Searching for any inspection with 'Hume'...")
            inspection = FoodSafetyAgencyInspection.objects.filter(
                client_name__icontains='Hume'
            ).first()

        if not inspection:
            print("   ❌ No inspection found for Hume!")
            return False

        print(f"   ✅ Found inspection:")
        print(f"      ID: {inspection.id}")
        print(f"      Client: {inspection.client_name}")
        print(f"      Date: {inspection.date_of_inspection}")
        print(f"      Inspector: {inspection.inspector_name}")

        # Create upload directory if it doesn't exist
        upload_dir = BASE_DIR / 'media' / 'uploads' / 'inspections'
        upload_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n2. Upload directory: {upload_dir}")

        # Generate group_id (client_name + date)
        from django.utils.text import slugify
        client_slug = slugify(inspection.client_name).replace('-', '_')
        date_str = inspection.date_of_inspection.strftime('%Y%m%d')
        group_id = f"{client_slug}_{date_str}"

        print(f"   Group ID: {group_id}")

        # Upload RFI
        print("\n3. 📄 Uploading RFI document...")
        rfi_filename = f"RFI_{group_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        rfi_path = upload_dir / rfi_filename

        with open(rfi_path, 'wb') as f:
            f.write(create_fake_pdf(rfi_filename))

        # Update inspection with RFI upload tracking
        inspection.rfi_uploaded_date = datetime.now()
        inspection.save()

        print(f"   ✅ RFI uploaded: {rfi_filename}")
        print(f"   📁 Path: {rfi_path}")
        print(f"   📅 Upload date set: {inspection.rfi_uploaded_date}")
        print(f"   🟢 RFI button should now be GREEN in browser!")

        # Upload Invoice
        print("\n4. 💰 Uploading Invoice document...")
        invoice_filename = f"INVOICE_{group_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        invoice_path = upload_dir / invoice_filename

        with open(invoice_path, 'wb') as f:
            f.write(create_fake_pdf(invoice_filename))

        # Update inspection with Invoice upload tracking
        inspection.invoice_uploaded_date = datetime.now()
        inspection.save()

        print(f"   ✅ Invoice uploaded: {invoice_filename}")
        print(f"   📁 Path: {invoice_path}")
        print(f"   📅 Upload date set: {inspection.invoice_uploaded_date}")
        print(f"   🟢 Invoice button should now be GREEN in browser!")

        # Upload Compliance Document
        print("\n5. 📋 Uploading Compliance document...")
        compliance_filename = f"COMPLIANCE_{group_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        compliance_path = upload_dir / compliance_filename

        with open(compliance_path, 'wb') as f:
            f.write(create_fake_pdf(compliance_filename))

        # Mark as having compliance document
        inspection.is_direction_present_for_this_inspection = False  # Compliant
        inspection.save()

        print(f"   ✅ Compliance uploaded: {compliance_filename}")
        print(f"   📁 Path: {compliance_path}")
        print(f"   🟢 View Files button should now be GREEN in browser!")

        # Clear compliance status cache to reflect new uploads
        print("\n6. 🔄 Clearing compliance status cache...")
        cache_key = f"compliance_status_{inspection.client_name}_{inspection.date_of_inspection}"
        cache.delete(cache_key)
        onedrive_cache_key = f"onedrive_compliance_{inspection.client_name}_{inspection.date_of_inspection}"
        cache.delete(onedrive_cache_key)
        print(f"   ✅ Cache cleared for keys:")
        print(f"      - {cache_key}")
        print(f"      - {onedrive_cache_key}")

        print("\n" + "="*60)
        print("✅ ALL FILES UPLOADED SUCCESSFULLY!")
        print("="*60)
        print("\n🔄 REFRESH YOUR BROWSER to see the color changes:")
        print("   🟢 RFI button → GREEN with checkmark")
        print("   🟢 Invoice button → GREEN with checkmark")
        print("   🟢 View Files button → GREEN (complete)")
        print("\n📊 Inspection Details:")
        print(f"   Client: {inspection.client_name}")
        print(f"   Date: {inspection.date_of_inspection}")
        print(f"   RFI Upload Date: {inspection.rfi_uploaded_date}")
        print(f"   Invoice Upload Date: {inspection.invoice_uploaded_date}")
        print(f"\n✨ Files created in: {upload_dir}")
        print("\nNOTE: The button colors are controlled by checking if the")
        print("      rfi_uploaded_date and invoice_uploaded_date fields exist.")
        print("      The database has been updated with these dates.")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n🚀 Starting file upload process...")
    print("This will upload RFI, Invoice, and Compliance files")
    print("for the Hume International inspection.\n")

    success = upload_files_for_hume()

    if success:
        print("\n✅ Process completed successfully!")
        print("\n👉 NEXT STEP: Refresh your browser (F5) to see the GREEN buttons!")
    else:
        print("\n❌ Process failed. Please check the errors above.")

    sys.exit(0 if success else 1)
