#!/usr/bin/env python3
"""
Test script for find_misplaced_files.py
Creates a test media folder structure with intentional issues to verify the scanner works correctly.
"""

import os
import shutil
from pathlib import Path


def create_test_structure(test_root='./test_media'):
    """Create a test media folder structure with both correct and incorrect examples."""
    test_root = Path(test_root)

    # Clean up existing test folder
    if test_root.exists():
        print(f"Cleaning up existing test folder: {test_root}")
        shutil.rmtree(test_root)

    print(f"\nCreating test media folder structure: {test_root}\n")

    # =========================================================================
    # CORRECT STRUCTURE
    # =========================================================================
    print("[OK] Creating CORRECT file structures...")

    # Example 1: Correct structure
    correct_path_1 = test_root / '2025' / 'January' / 'ABC Dairy Inc' / '2025-01-15' / 'Inspection-001' / 'Compliance'
    correct_path_1.mkdir(parents=True, exist_ok=True)
    (correct_path_1 / 'compliance_doc_1.pdf').touch()
    print(f"   Created: {correct_path_1.relative_to(test_root)}/compliance_doc_1.pdf")

    # Example 2: Correct structure with RFI
    correct_path_2 = test_root / '2025' / 'February' / 'XYZ Foods Ltd' / '2025-02-20' / 'Inspection-002' / 'Request For Invoice'
    correct_path_2.mkdir(parents=True, exist_ok=True)
    (correct_path_2 / 'rfi_document.pdf').touch()
    print(f"   Created: {correct_path_2.relative_to(test_root)}/rfi_document.pdf")

    # Example 3: Correct structure with invoice
    correct_path_3 = test_root / '2025' / 'March' / 'Fresh Produce Co' / '2025-03-10' / 'Inspection-003' / 'invoice'
    correct_path_3.mkdir(parents=True, exist_ok=True)
    (correct_path_3 / 'invoice_001.pdf').touch()
    print(f"   Created: {correct_path_3.relative_to(test_root)}/invoice_001.pdf")

    # Example 4: Correct structure with lab results subfolder
    correct_path_4 = test_root / '2025' / 'April' / 'Organic Farms LLC' / '2025-04-05' / 'Inspection-004' / 'lab results' / 'subfolder'
    correct_path_4.mkdir(parents=True, exist_ok=True)
    (correct_path_4 / 'lab_result_1.pdf').touch()
    print(f"   Created: {correct_path_4.relative_to(test_root)}/lab_result_1.pdf")

    # =========================================================================
    # INCORRECT STRUCTURES (Issues to detect)
    # =========================================================================
    print("\n[ISSUES] Creating INCORRECT file structures (intentional issues)...")

    # Issue 1: File too shallow (at root level)
    issue_1 = test_root / 'orphan_file.pdf'
    issue_1.touch()
    print(f"   Issue 1 - File at root: {issue_1.relative_to(test_root)}")

    # Issue 2: File in year folder (too shallow)
    issue_2 = test_root / '2025' / 'misplaced_in_year.pdf'
    issue_2.parent.mkdir(parents=True, exist_ok=True)
    issue_2.touch()
    print(f"   Issue 2 - File in year folder: {issue_2.relative_to(test_root)}")

    # Issue 3: Invalid year folder name
    issue_3_path = test_root / 'Year2025' / 'January' / 'Client A' / '2025-01-01' / 'Inspection-001' / 'Compliance'
    issue_3_path.mkdir(parents=True, exist_ok=True)
    (issue_3_path / 'doc.pdf').touch()
    print(f"   Issue 3 - Invalid year folder: Year2025")

    # Issue 4: Invalid month folder name
    issue_4_path = test_root / '2025' / 'Jan' / 'Client B' / '2025-01-15' / 'Inspection-002' / 'invoice'
    issue_4_path.mkdir(parents=True, exist_ok=True)
    (issue_4_path / 'invoice.pdf').touch()
    print(f"   Issue 4 - Invalid month folder: Jan (should be January)")

    # Issue 5: Empty client folder name (Windows doesn't allow folders with trailing spaces)
    issue_5_path = test_root / '2025' / 'May' / 'Client-With-Dashes' / '2025-05-20' / 'Inspection-003' / 'Compliance'
    issue_5_path.mkdir(parents=True, exist_ok=True)
    (issue_5_path / 'compliance.pdf').touch()
    print(f"   Issue 5 - Client folder name with dashes: 'Client-With-Dashes' (unusual but valid)")

    # Issue 6: Invalid date folder format
    issue_6_path = test_root / '2025' / 'June' / 'Client D' / '2025_06_15' / 'Inspection-004' / 'invoice'
    issue_6_path.mkdir(parents=True, exist_ok=True)
    (issue_6_path / 'invoice.pdf').touch()
    print(f"   Issue 6 - Invalid date format: 2025_06_15 (should be 2025-06-15)")

    # Issue 7: Invalid inspection folder name (missing 'Inspection-' prefix)
    issue_7_path = test_root / '2025' / 'July' / 'Client E' / '2025-07-10' / 'Insp-005' / 'Compliance'
    issue_7_path.mkdir(parents=True, exist_ok=True)
    (issue_7_path / 'compliance.pdf').touch()
    print(f"   Issue 7 - Invalid inspection folder: Insp-005 (should be Inspection-XXX)")

    # Issue 8: Unexpected document type folder
    issue_8_path = test_root / '2025' / 'August' / 'Client F' / '2025-08-25' / 'Inspection-006' / 'random_docs'
    issue_8_path.mkdir(parents=True, exist_ok=True)
    (issue_8_path / 'random.pdf').touch()
    print(f"   Issue 8 - Unexpected doc type folder: random_docs")

    # Issue 9: File in month folder (too shallow)
    issue_9 = test_root / '2025' / 'September' / 'loose_file.pdf'
    issue_9.parent.mkdir(parents=True, exist_ok=True)
    issue_9.touch()
    print(f"   Issue 9 - File in month folder: {issue_9.relative_to(test_root)}")

    # Issue 10: File in client folder (too shallow)
    issue_10 = test_root / '2025' / 'October' / 'Client G' / 'misplaced.pdf'
    issue_10.parent.mkdir(parents=True, exist_ok=True)
    issue_10.touch()
    print(f"   Issue 10 - File in client folder: {issue_10.relative_to(test_root)}")

    print(f"\n[SUCCESS] Test media folder structure created successfully!")
    print(f"   Location: {test_root.absolute()}")
    print(f"\n[SUMMARY] Summary:")
    print(f"   - Correct structures: 4")
    print(f"   - Intentional issues: 10")
    print(f"\nYou can now run: python find_misplaced_files.py --media-root {test_root}")

    return test_root


def main():
    """Main function."""
    print("\n" + "="*80)
    print("TEST MEDIA FOLDER CREATOR")
    print("="*80)

    test_root = create_test_structure('./test_media')

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. Run the scanner on the test folder:")
    print(f"   python find_misplaced_files.py --media-root {test_root}")
    print("\n2. Export detailed report:")
    print(f"   python find_misplaced_files.py --media-root {test_root} --export-report test_report.json")
    print("\n3. Once verified, run on actual media folder:")
    print(f"   python find_misplaced_files.py --media-root ./media")
    print()


if __name__ == '__main__':
    main()
