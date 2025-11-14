#!/usr/bin/env python3
"""
Test script to show exactly how compliance documents will be pulled from Google Drive
"""

from datetime import datetime, timedelta

def get_target_months():
    """Get list of months from October 1, 2025 onwards"""

    # START DATE: October 1, 2025
    start_month = datetime(2025, 10, 1)
    current_date = datetime.now()

    # Generate list of month names from October 2025 to current month + ~2 months ahead
    target_months = []
    temp_date = start_month
    while temp_date <= current_date.replace(day=1) + timedelta(days=62):
        month_name = temp_date.strftime('%B %Y')  # e.g., "October 2025"
        target_months.append(month_name)
        # Move to next month
        if temp_date.month == 12:
            temp_date = datetime(temp_date.year + 1, 1, 1)
        else:
            temp_date = datetime(temp_date.year, temp_date.month + 1, 1)

    return target_months

if __name__ == '__main__':
    print("=" * 80)
    print("COMPLIANCE DOCUMENTS PULL CONFIGURATION")
    print("=" * 80)
    print()

    current_date = datetime.now()
    print(f"Today's Date: {current_date.strftime('%B %d, %Y')}")
    print()

    print("=" * 80)
    print("GOOGLE DRIVE FOLDER STRUCTURE")
    print("=" * 80)
    print()
    print("Parent Folder: Organized Files/2025")
    print("Folder ID: 1pzot8MQ-m3u0f9-BWxpBO40QgLmeZhRP")
    print()

    target_months = get_target_months()

    print("=" * 80)
    print("MONTHS TO PULL FROM (DYNAMIC)")
    print("=" * 80)
    print()
    print(f"Start: October 1, 2025")
    print(f"End: Current month + ~2 months ahead")
    print()
    print(f"Total Month Folders: {len(target_months)}")
    print()

    for i, month in enumerate(target_months, 1):
        print(f"  {i}. {month} folder")
        print(f"     >> Files in this folder will be pulled for {month} inspections")
        print()

    print("=" * 80)
    print("HOW IT WORKS")
    print("=" * 80)
    print()
    print("1. System looks in: Organized Files/2025/")
    print()
    print("2. Finds folders named:")
    for month in target_months:
        print(f"   - '{month}'")
    print()
    print("3. Pulls ALL files from these month folders")
    print()
    print("4. Matches files to inspections based on:")
    print("   - Account code")
    print("   - Commodity")
    print("   - Date (within 15 days)")
    print()
    print("5. Downloads files to local 'Compliance' folders")
    print()

    print("=" * 80)
    print("EXAMPLE")
    print("=" * 80)
    print()
    print("If you have an inspection on October 15, 2025:")
    print("  >> System pulls files from 'October 2025' folder")
    print()
    print("If you have an inspection on November 20, 2025:")
    print("  >> System pulls files from 'November 2025' folder")
    print()
    print("If you have an inspection on December 5, 2025:")
    print("  >> System pulls files from 'December 2025' folder")
    print()

    print("=" * 80)
    print("AUTO-UPDATE FEATURE")
    print("=" * 80)
    print()
    print("[OK] NO MANUAL UPDATES NEEDED!")
    print()
    print("When you create new month folders (January 2026, February 2026, etc.)")
    print("the system will AUTOMATICALLY include them.")
    print()
    print("Example timeline:")
    print(f"  - Today ({current_date.strftime('%B %d, %Y')}): Pulls from {len(target_months)} months")
    print(f"  - December 2025: Will pull from October 2025 through February 2026")
    print(f"  - January 2026: Will pull from October 2025 through March 2026")
    print()
