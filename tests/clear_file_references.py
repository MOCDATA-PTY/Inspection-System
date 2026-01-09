#!/usr/bin/env python3
"""
Script to clear all file upload references from inspections
This will reset all upload tracking fields (uploaded_by, uploaded_date)
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

if __name__ == '__main__':
    print("=" * 80)
    print("CLEARING ALL FILE UPLOAD REFERENCES")
    print("=" * 80)
    print()

    inspections = FoodSafetyAgencyInspection.objects.all()
    total_count = inspections.count()

    print(f"Total inspections: {total_count}")
    print()

    # Count how many have uploads before clearing
    rfi_count = inspections.filter(rfi_uploaded_date__isnull=False).count()
    invoice_count = inspections.filter(invoice_uploaded_date__isnull=False).count()
    composition_count = inspections.filter(composition_uploaded_date__isnull=False).count()
    occurrence_count = inspections.filter(occurrence_uploaded_date__isnull=False).count()
    coa_count = inspections.filter(coa_uploaded_date__isnull=False).count()
    lab_form_count = inspections.filter(lab_form_uploaded_date__isnull=False).count()
    retest_count = inspections.filter(retest_uploaded_date__isnull=False).count()

    print("Current upload counts:")
    print(f"  RFI documents: {rfi_count}")
    print(f"  Invoice documents: {invoice_count}")
    print(f"  Composition documents: {composition_count}")
    print(f"  Occurrence documents: {occurrence_count}")
    print(f"  COA documents: {coa_count}")
    print(f"  Lab Form documents: {lab_form_count}")
    print(f"  Retest documents: {retest_count}")
    print()

    print("Clearing all file upload references...")
    print()

    # Clear all upload tracking fields
    updated = inspections.update(
        rfi_uploaded_by=None,
        rfi_uploaded_date=None,
        invoice_uploaded_by=None,
        invoice_uploaded_date=None,
        composition_uploaded_by=None,
        composition_uploaded_date=None,
        occurrence_uploaded_by=None,
        occurrence_uploaded_date=None,
        coa_uploaded_by=None,
        coa_uploaded_date=None,
        lab_form_uploaded_by=None,
        lab_form_uploaded_date=None,
        retest_uploaded_by=None,
        retest_uploaded_date=None
    )

    print(f"[SUCCESS] Cleared file upload references from {updated} inspections")
    print()
    print("All upload tracking fields have been reset:")
    print("  - RFI uploads (uploaded_by, uploaded_date)")
    print("  - Invoice uploads (uploaded_by, uploaded_date)")
    print("  - Composition uploads (uploaded_by, uploaded_date)")
    print("  - Occurrence uploads (uploaded_by, uploaded_date)")
    print("  - COA uploads (uploaded_by, uploaded_date)")
    print("  - Lab Form uploads (uploaded_by, uploaded_date)")
    print("  - Retest uploads (uploaded_by, uploaded_date)")
    print()

    # Verify the clear worked
    rfi_after = inspections.filter(rfi_uploaded_date__isnull=False).count()
    invoice_after = inspections.filter(invoice_uploaded_date__isnull=False).count()
    composition_after = inspections.filter(composition_uploaded_date__isnull=False).count()
    occurrence_after = inspections.filter(occurrence_uploaded_date__isnull=False).count()

    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    print(f"Inspections with RFI uploads remaining: {rfi_after}")
    print(f"Inspections with Invoice uploads remaining: {invoice_after}")
    print(f"Inspections with Composition uploads remaining: {composition_after}")
    print(f"Inspections with Occurrence uploads remaining: {occurrence_after}")
    print()

    if rfi_after == 0 and invoice_after == 0 and composition_after == 0 and occurrence_after == 0:
        print("[SUCCESS] All file references cleared successfully!")
    else:
        print("[WARNING] Some file references may still exist")

    print()
    print("=" * 80)
    print("NEXT STEP: Delete the media folder on the server")
    print("Run: sudo rm -rf /root/Inspection-System/media/inspection/")
    print("=" * 80)
