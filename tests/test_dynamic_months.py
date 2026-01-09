#!/usr/bin/env python3
"""
Test script to verify which months are dynamically selected for compliance document pulling
"""

from datetime import datetime, timedelta

def get_target_months():
    """Get list of months from October 2025 to current month + ~2 months ahead"""

    # Dynamically determine which months to pull from (October 2025 onwards)
    start_month = datetime(2025, 10, 1)  # October 2025
    current_date = datetime.now()

    # Generate list of month names from October 2025 to current month + 1 month ahead
    target_months = []
    temp_date = start_month
    while temp_date <= current_date.replace(day=1) + timedelta(days=62):  # Current + ~2 months
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
    print("DYNAMIC MONTH SELECTION TEST")
    print("=" * 80)
    print()

    current_date = datetime.now()
    print(f"Current Date: {current_date.strftime('%B %d, %Y')}")
    print(f"Start Month: October 2025")
    print()

    target_months = get_target_months()

    print(f"Total Months to Pull From: {len(target_months)}")
    print()
    print("Months that will be pulled:")
    for i, month in enumerate(target_months, 1):
        print(f"  {i}. {month}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"The system will automatically pull compliance documents from:")
    print(f"  - October 2025 through {target_months[-1]}")
    print()
    print("As new months are added to Google Drive, the system will automatically")
    print("include them without any code changes needed!")
    print()
