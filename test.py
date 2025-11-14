#!/usr/bin/env python3
"""
Test script to verify RFI and Invoice file detection for both old and new naming conventions
"""
import os
import django
import sys
from pathlib import Path

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection

def test_filename_detection(filename):
    """Test if a filename matches old or new naming conventions"""
    filename_lower = filename.lower()

    results = {
        'filename': filename,
        'rfi_old': 'rfi' in filename_lower and not filename_lower.startswith('fsa-rfi'),
        'rfi_new': filename_lower.startswith('fsa-rfi'),
        'invoice_old': ('inv' in filename_lower or 'invoice' in filename_lower) and not filename_lower.startswith('fsa-inv'),
        'invoice_new': filename_lower.startswith('fsa-inv'),
        'lab_old': 'lab' in filename_lower and not filename_lower.startswith('fsl-'),
        'lab_new': filename_lower.startswith('fsl-'),
    }

    return results

def scan_inspection_folders():
    """Scan the media folder for inspection files"""
    media_root = settings.MEDIA_ROOT
    inspection_path = os.path.join(media_root, 'inspection')

    print("\n" + "=" * 100)
    print("SCANNING INSPECTION FOLDERS FOR RFI AND INVOICE FILES")
    print("=" * 100)
    print(f"\nMedia Root: {media_root}")
    print(f"Inspection Path: {inspection_path}")
    print(f"Path Exists: {os.path.exists(inspection_path)}")

    if not os.path.exists(inspection_path):
        print("\nERROR: Inspection path does not exist!")
        return

    rfi_files = []
    invoice_files = []
    lab_files = []

    # Walk through all directories
    for root, dirs, files in os.walk(inspection_path):
        for filename in files:
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, inspection_path)

                # Check if it's in an RFI folder
                if 'rfi' in root.lower() or 'request for invoice' in root.lower():
                    detection = test_filename_detection(filename)
                    rfi_files.append({
                        'path': relative_path,
                        'filename': filename,
                        'detection': detection
                    })

                # Check if it's in an Invoice folder
                if 'invoice' in root.lower():
                    detection = test_filename_detection(filename)
                    invoice_files.append({
                        'path': relative_path,
                        'filename': filename,
                        'detection': detection
                    })

                # Check if it's in a Lab folder
                if 'lab' in root.lower():
                    detection = test_filename_detection(filename)
                    lab_files.append({
                        'path': relative_path,
                        'filename': filename,
                        'detection': detection
                    })

    # Print RFI files
    print("\n" + "=" * 100)
    print(f"RFI FILES FOUND: {len(rfi_files)}")
    print("=" * 100)

    if rfi_files:
        for idx, file_info in enumerate(rfi_files[:20], 1):  # Show first 20
            print(f"\n[{idx}] {file_info['filename']}")
            print(f"    Path: {file_info['path']}")
            detection = file_info['detection']
            if detection['rfi_new']:
                print(f"    [OK] Detected as: NEW RFI (FSA-RFI-XX-XXXXXX)")
            elif detection['rfi_old']:
                print(f"    [OK] Detected as: OLD RFI (contains 'rfi')")
            else:
                print(f"    [FAIL] NOT DETECTED - filename doesn't match patterns!")

        if len(rfi_files) > 20:
            print(f"\n... and {len(rfi_files) - 20} more RFI files")
    else:
        print("\nNo RFI files found in inspection folders")

    # Print Invoice files
    print("\n" + "=" * 100)
    print(f"INVOICE FILES FOUND: {len(invoice_files)}")
    print("=" * 100)

    if invoice_files:
        for idx, file_info in enumerate(invoice_files[:20], 1):
            print(f"\n[{idx}] {file_info['filename']}")
            print(f"    Path: {file_info['path']}")
            detection = file_info['detection']
            if detection['invoice_new']:
                print(f"    [OK] Detected as: NEW INVOICE (FSA-INV-XX-XXXXXX)")
            elif detection['invoice_old']:
                print(f"    [OK] Detected as: OLD INVOICE (contains 'inv' or 'invoice')")
            else:
                print(f"    [FAIL] NOT DETECTED - filename doesn't match patterns!")

        if len(invoice_files) > 20:
            print(f"\n... and {len(invoice_files) - 20} more Invoice files")
    else:
        print("\nNo Invoice files found in inspection folders")

    # Print Lab files
    print("\n" + "=" * 100)
    print(f"LAB/COA FILES FOUND: {len(lab_files)}")
    print("=" * 100)

    if lab_files:
        for idx, file_info in enumerate(lab_files[:20], 1):
            print(f"\n[{idx}] {file_info['filename']}")
            print(f"    Path: {file_info['path']}")
            detection = file_info['detection']
            if detection['lab_new']:
                print(f"    [OK] Detected as: NEW LAB (FSL-COMMODITY-XX-XXXXXX)")
            elif detection['lab_old']:
                print(f"    [OK] Detected as: OLD LAB (contains 'lab')")
            else:
                print(f"    [FAIL] NOT DETECTED - filename doesn't match patterns!")

        if len(lab_files) > 20:
            print(f"\n... and {len(lab_files) - 20} more Lab files")
    else:
        print("\nNo Lab files found in inspection folders")

    # Summary
    print("\n" + "=" * 100)
    print("DETECTION SUMMARY")
    print("=" * 100)

    # Count old vs new
    rfi_old_count = sum(1 for f in rfi_files if f['detection']['rfi_old'])
    rfi_new_count = sum(1 for f in rfi_files if f['detection']['rfi_new'])
    invoice_old_count = sum(1 for f in invoice_files if f['detection']['invoice_old'])
    invoice_new_count = sum(1 for f in invoice_files if f['detection']['invoice_new'])
    lab_old_count = sum(1 for f in lab_files if f['detection']['lab_old'])
    lab_new_count = sum(1 for f in lab_files if f['detection']['lab_new'])

    print(f"\nRFI Files:")
    print(f"  Old naming convention: {rfi_old_count}")
    print(f"  New naming convention (FSA-RFI): {rfi_new_count}")
    print(f"  Total: {len(rfi_files)}")

    print(f"\nInvoice Files:")
    print(f"  Old naming convention: {invoice_old_count}")
    print(f"  New naming convention (FSA-INV): {invoice_new_count}")
    print(f"  Total: {len(invoice_files)}")

    print(f"\nLab/COA Files:")
    print(f"  Old naming convention: {lab_old_count}")
    print(f"  New naming convention (FSL-): {lab_new_count}")
    print(f"  Total: {len(lab_files)}")

    print("\n" + "=" * 100)
    print("TEST COMPLETED")
    print("=" * 100 + "\n")

if __name__ == "__main__":
    try:
        scan_inspection_folders()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
