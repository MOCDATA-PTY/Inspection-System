#!/usr/bin/env python
"""Test the file checking function"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from datetime import datetime
from django.conf import settings

# Test the check_group_files function logic
def check_group_files(client_name, inspection_date):
    """Check if files exist for this group - optimized for speed"""
    import re

    try:
        # Get inspection base path - use MEDIA_ROOT/inspection where files are actually uploaded
        inspection_base = os.path.join(settings.MEDIA_ROOT, 'inspection')

        # Sanitize client name to match folder structure
        def create_folder_name(name):
            if not name:
                return "unknown_client"
            clean_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)
            clean_name = clean_name.replace(' ', '_').replace('-', '_')
            clean_name = re.sub(r'_+', '_', clean_name)
            clean_name = clean_name.strip('_').lower()
            return clean_name or "unknown_client"

        sanitized_client_name = create_folder_name(client_name)
        name_with_spaces_for_apostrophe = client_name.replace("'", ' ')
        sanitized_with_apostrophe = create_folder_name(name_with_spaces_for_apostrophe)
        client_folder_variations = [sanitized_client_name, sanitized_with_apostrophe, client_name]

        # Get year and month from inspection date
        year = inspection_date.strftime('%Y')
        month = inspection_date.strftime('%B')
        parent_path = os.path.join(inspection_base, year, month)

        print(f"Checking: {client_name}")
        print(f"  Date: {inspection_date}")
        print(f"  Parent path: {parent_path}")
        print(f"  Exists: {os.path.exists(parent_path)}")

        has_rfi = has_invoice = has_lab = has_compliance = False

        if os.path.exists(parent_path):
            for folder_variation in client_folder_variations:
                test_path = os.path.join(parent_path, folder_variation)
                if os.path.exists(test_path):
                    print(f"  Found folder: {test_path}")
                    # Quick check for RFI (check main variations only)
                    if not has_rfi:
                        for rfi_var in ['RFI', 'rfi']:
                            rfi_path = os.path.join(test_path, rfi_var)
                            if os.path.exists(rfi_path) and os.listdir(rfi_path):
                                has_rfi = True
                                print(f"    Found RFI: {rfi_path}")
                                break

                    # Quick check for Invoice
                    if not has_invoice:
                        for inv_var in ['Invoice', 'invoice']:
                            invoice_path = os.path.join(test_path, inv_var)
                            if os.path.exists(invoice_path) and os.listdir(invoice_path):
                                has_invoice = True
                                print(f"    Found Invoice: {invoice_path}")
                                break

                    # If we found all files, no need to check other variations
                    if has_rfi and has_invoice:
                        break

        # Determine file status
        if has_rfi and has_invoice:
            file_status = 'all_files'  # Green
        elif has_rfi or has_invoice:
            file_status = 'partial_files'  # Orange
        else:
            file_status = 'no_files'  # Red

        print(f"  Result: RFI={has_rfi}, Invoice={has_invoice}, Status={file_status}")
        return {
            'has_rfi': has_rfi,
            'has_invoice': has_invoice,
            'has_lab': has_lab,
            'has_compliance': has_compliance,
            'file_status': file_status
        }
    except Exception as e:
        print(f"[FILE CHECK ERROR] {client_name} on {inspection_date}: {e}")
        import traceback
        traceback.print_exc()
        return {
            'has_rfi': False,
            'has_invoice': False,
            'has_lab': False,
            'has_compliance': False,
            'file_status': 'no_files'
        }

# Test with a sample client and date
test_date = datetime(2025, 11, 27).date()
result = check_group_files("Food Lover's Market - Knysna", test_date)
print("\n" + "="*80)
print("FINAL RESULT:")
print(result)
