"""
Test script to simulate document uploads and verify color changes
This script creates fake/test files to test the button color changes without affecting real data.

WARNING: This is for TESTING purposes only!
Run this in a development/test environment, NOT in production.
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
from main.models import Inspection
from django.core.files.base import ContentFile


class TestDocumentUploader:
    """Test class for simulating document uploads"""

    def __init__(self):
        self.test_results = []
        self.created_files = []

    def create_fake_pdf(self, filename):
        """
        Create a minimal fake PDF file for testing
        This creates a simple text file that mimics a PDF
        """
        # Minimal PDF header (not a real PDF, but good enough for testing)
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
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Document) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000214 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
314
%%EOF
"""
        return ContentFile(fake_pdf_content, name=filename)

    def list_available_inspections(self):
        """List available inspections that can be used for testing"""
        print("\n" + "="*60)
        print("AVAILABLE INSPECTIONS FOR TESTING")
        print("="*60)

        inspections = Inspection.objects.all()[:10]  # Get first 10

        if not inspections:
            print("❌ No inspections found in database!")
            print("   Please create some inspections first.")
            return []

        print(f"\nFound {inspections.count()} inspection(s). Showing first 10:\n")

        for i, inspection in enumerate(inspections, 1):
            print(f"{i}. ID: {inspection.remote_id}")
            print(f"   Client: {inspection.client_name}")
            print(f"   Date: {inspection.date_of_inspection}")
            print(f"   RFI Uploaded: {'✓ Yes' if inspection.rfi_uploaded else '✗ No'}")
            print(f"   Invoice Uploaded: {'✓ Yes' if inspection.invoice_uploaded else '✗ No'}")
            print(f"   Compliance File: {'✓ Yes' if inspection.compliance_file else '✗ No'}")
            print("-" * 40)

        return list(inspections)

    def upload_rfi(self, inspection_id):
        """Upload a fake RFI document to an inspection"""
        try:
            inspection = Inspection.objects.get(remote_id=inspection_id)

            print(f"\n📄 Uploading RFI for inspection {inspection_id}...")
            print(f"   Client: {inspection.client_name}")

            # Create fake RFI file
            fake_rfi = self.create_fake_pdf(f"RFI_{inspection_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

            # Upload the file
            inspection.rfi_file = fake_rfi
            inspection.rfi_uploaded = True
            inspection.save()

            self.created_files.append(inspection.rfi_file.path)

            print(f"   ✅ RFI uploaded successfully!")
            print(f"   File path: {inspection.rfi_file.path}")
            print(f"   🟢 RFI button should now be GREEN")

            self.test_results.append({
                'inspection_id': inspection_id,
                'type': 'RFI',
                'status': 'success',
                'file_path': inspection.rfi_file.path
            })

            return True

        except Inspection.DoesNotExist:
            print(f"   ❌ Inspection {inspection_id} not found!")
            return False
        except Exception as e:
            print(f"   ❌ Error uploading RFI: {e}")
            return False

    def upload_invoice(self, inspection_id):
        """Upload a fake Invoice document to an inspection"""
        try:
            inspection = Inspection.objects.get(remote_id=inspection_id)

            print(f"\n💰 Uploading Invoice for inspection {inspection_id}...")
            print(f"   Client: {inspection.client_name}")

            # Create fake invoice file
            fake_invoice = self.create_fake_pdf(f"INVOICE_{inspection_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

            # Upload the file
            inspection.invoice_file = fake_invoice
            inspection.invoice_uploaded = True
            inspection.save()

            self.created_files.append(inspection.invoice_file.path)

            print(f"   ✅ Invoice uploaded successfully!")
            print(f"   File path: {inspection.invoice_file.path}")
            print(f"   🟢 Invoice button should now be GREEN")

            self.test_results.append({
                'inspection_id': inspection_id,
                'type': 'Invoice',
                'status': 'success',
                'file_path': inspection.invoice_file.path
            })

            return True

        except Inspection.DoesNotExist:
            print(f"   ❌ Inspection {inspection_id} not found!")
            return False
        except Exception as e:
            print(f"   ❌ Error uploading Invoice: {e}")
            return False

    def upload_compliance(self, inspection_id):
        """Upload a fake Compliance document to an inspection"""
        try:
            inspection = Inspection.objects.get(remote_id=inspection_id)

            print(f"\n📋 Uploading Compliance file for inspection {inspection_id}...")
            print(f"   Client: {inspection.client_name}")

            # Create fake compliance file
            fake_compliance = self.create_fake_pdf(f"COMPLIANCE_{inspection_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

            # Upload the file
            inspection.compliance_file = fake_compliance
            inspection.save()

            self.created_files.append(inspection.compliance_file.path)

            print(f"   ✅ Compliance file uploaded successfully!")
            print(f"   File path: {inspection.compliance_file.path}")
            print(f"   🟡 View Files button should now be YELLOW/ORANGE (partial)")

            self.test_results.append({
                'inspection_id': inspection_id,
                'type': 'Compliance',
                'status': 'success',
                'file_path': inspection.compliance_file.path
            })

            return True

        except Inspection.DoesNotExist:
            print(f"   ❌ Inspection {inspection_id} not found!")
            return False
        except Exception as e:
            print(f"   ❌ Error uploading Compliance: {e}")
            return False

    def remove_test_files(self):
        """Remove all test files that were created"""
        print("\n" + "="*60)
        print("CLEANUP: Removing test files")
        print("="*60)

        for file_path in self.created_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"   ✓ Deleted: {file_path}")
                else:
                    print(f"   ⚠ File not found: {file_path}")
            except Exception as e:
                print(f"   ✗ Error deleting {file_path}: {e}")

        print(f"\n   Cleanup complete! Removed {len(self.created_files)} file(s)")

    def reset_inspection(self, inspection_id):
        """Reset an inspection to remove all uploaded files"""
        try:
            inspection = Inspection.objects.get(remote_id=inspection_id)

            print(f"\n🔄 Resetting inspection {inspection_id}...")

            # Remove files if they exist
            if inspection.rfi_file:
                inspection.rfi_file.delete()
            if inspection.invoice_file:
                inspection.invoice_file.delete()
            if inspection.compliance_file:
                inspection.compliance_file.delete()

            # Reset flags
            inspection.rfi_uploaded = False
            inspection.invoice_uploaded = False
            inspection.save()

            print(f"   ✅ Inspection reset successfully!")
            print(f"   All buttons should now be GRAY (default state)")

            return True

        except Inspection.DoesNotExist:
            print(f"   ❌ Inspection {inspection_id} not found!")
            return False
        except Exception as e:
            print(f"   ❌ Error resetting inspection: {e}")
            return False

    def print_summary(self):
        """Print a summary of all test operations"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        if not self.test_results:
            print("No tests were run.")
            return

        print(f"\nTotal operations: {len(self.test_results)}")

        successful = sum(1 for r in self.test_results if r['status'] == 'success')
        failed = len(self.test_results) - successful

        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")

        print("\nDetailed results:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"{status_icon} {result['type']} - Inspection {result['inspection_id']}")


def interactive_menu():
    """Interactive menu for testing document uploads"""
    uploader = TestDocumentUploader()

    print("\n" + "="*60)
    print("DOCUMENT UPLOAD TEST SCRIPT")
    print("="*60)
    print("\nThis script allows you to test document uploads and see")
    print("the color changes in the inspection table.")
    print("\n⚠️  WARNING: Use only in development/test environment!")

    while True:
        print("\n" + "-"*60)
        print("MENU OPTIONS:")
        print("-"*60)
        print("1. List available inspections")
        print("2. Upload RFI document")
        print("3. Upload Invoice document")
        print("4. Upload Compliance file")
        print("5. Upload ALL documents (RFI + Invoice + Compliance)")
        print("6. Reset an inspection (remove all files)")
        print("7. View test summary")
        print("8. Cleanup and exit")
        print("0. Exit without cleanup")

        choice = input("\nEnter your choice (0-8): ").strip()

        if choice == '1':
            uploader.list_available_inspections()

        elif choice == '2':
            inspection_id = input("Enter inspection ID: ").strip()
            uploader.upload_rfi(inspection_id)

        elif choice == '3':
            inspection_id = input("Enter inspection ID: ").strip()
            uploader.upload_invoice(inspection_id)

        elif choice == '4':
            inspection_id = input("Enter inspection ID: ").strip()
            uploader.upload_compliance(inspection_id)

        elif choice == '5':
            inspection_id = input("Enter inspection ID: ").strip()
            print(f"\n📦 Uploading ALL documents for inspection {inspection_id}...")
            uploader.upload_rfi(inspection_id)
            uploader.upload_invoice(inspection_id)
            uploader.upload_compliance(inspection_id)
            print("\n✅ All documents uploaded!")
            print("   🟢 RFI button should be GREEN")
            print("   🟢 Invoice button should be GREEN")
            print("   🟢 View Files button should be GREEN (complete)")

        elif choice == '6':
            inspection_id = input("Enter inspection ID: ").strip()
            uploader.reset_inspection(inspection_id)

        elif choice == '7':
            uploader.print_summary()

        elif choice == '8':
            print("\nCleaning up test files...")
            uploader.remove_test_files()
            uploader.print_summary()
            print("\n✅ Cleanup complete. Goodbye!")
            break

        elif choice == '0':
            print("\n⚠️  Exiting without cleanup.")
            print("   Test files will remain in the system.")
            uploader.print_summary()
            print("\nGoodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")


def main():
    """Main function"""
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
