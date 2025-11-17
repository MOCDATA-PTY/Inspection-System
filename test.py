"""
Show inspections with client name '-' in clean table format
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection


def show_inspections_table():
    """Show inspections with '-' in clean table format"""

    # Get all inspections with client name '-' in November
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name="-",
        date_of_inspection__startswith="2025-11"
    ).order_by('date_of_inspection', 'remote_id')

    print("\n" + "="*140)
    print(" INSPECTIONS WITH CLIENT NAME '-' - NOVEMBER 2025")
    print("="*140)
    print(f"\nTotal: {inspections.count()} inspections\n")

    # Table header
    print("-"*140)
    print(f"{'ID':<6} {'Date':<12} {'Commodity':<10} {'Inspector':<20} {'Account Code':<25} {'Sample':<8} {'Product':<35}")
    print("-"*140)

    # Table rows
    for inspection in inspections:
        remote_id = str(inspection.remote_id)[:5]
        date = str(inspection.date_of_inspection)
        commodity = str(inspection.commodity)[:9]
        inspector = str(inspection.inspector_name)[:19]
        account = str(inspection.internal_account_code if inspection.internal_account_code else 'NONE')[:24]
        sample = str(inspection.is_sample_taken if inspection.is_sample_taken is not None else 'None')[:7]
        product = str(inspection.product_name)[:34] if inspection.product_name else ''

        print(f"{remote_id:<6} {date:<12} {commodity:<10} {inspector:<20} {account:<25} {sample:<8} {product:<35}")

    print("-"*140)

    # Summary by account code
    print("\n" + "="*140)
    print(" SUMMARY BY ACCOUNT CODE")
    print("="*140 + "\n")

    no_account = inspections.filter(internal_account_code__in=[None, '', '-']).count()
    has_account = inspections.exclude(internal_account_code__in=[None, '', '-']).count()

    print(f"No Account Code (or '-'):  {no_account} inspections")
    print(f"Has Account Code:          {has_account} inspections")

    if has_account > 0:
        print("\nAccount codes found:")
        unique_codes = set(inspections.exclude(internal_account_code__in=[None, '', '-']).values_list('internal_account_code', flat=True))
        for code in unique_codes:
            count = inspections.filter(internal_account_code=code).count()
            print(f"  - {code}: {count} inspection(s)")

    print("\n" + "="*140 + "\n")


if __name__ == "__main__":
    try:
        show_inspections_table()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
