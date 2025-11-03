#!/usr/bin/env python3
"""
Script to clear all uploaded file references from inspections
This will remove RFI, Invoice, Composition, and Occurrence file references
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

if __name__ == '__main__':
    print("=" * 80)
    print("CLEARING ALL UPLOADED FILE REFERENCES")
    print("=" * 80)
    print()

    inspections = FoodSafetyAgencyInspection.objects.all()
    total_count = inspections.count()

    print(f"Total inspections: {total_count}")
    print()
    print("Clearing file references...")
    print()

    # Clear all file fields
    updated = inspections.update(
        rfi_file='',
        invoice_file='',
        composition_file='',
        occurrence_file='',
        rfi_uploaded_by=None,
        rfi_uploaded_date=None,
        invoice_uploaded_by=None,
        invoice_uploaded_date=None,
        composition_uploaded_by=None,
        composition_uploaded_date=None
    )

    print(f"[SUCCESS] Cleared file references from {updated} inspections")
    print()
    print("File fields cleared:")
    print("  - RFI files")
    print("  - Invoice files")
    print("  - Composition files")
    print("  - Occurrence files")
    print("  - All upload metadata (uploaded_by, uploaded_date)")
    print()
    print("=" * 80)
    print("You can now delete the media/inspection folder safely")
    print("Run on server: sudo rm -rf /root/Inspection-System/media/inspection/")
    print("=" * 80)
