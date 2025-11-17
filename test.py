"""
Test script to pull 100 oldest inspections from the database
Shows Client Name, Account Code, and Inspection Date in a simple table format
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection


def main():
    """Main function to pull and display 100 oldest inspections in table format"""

    print("\n" + "="*120)
    print("100 OLDEST INSPECTIONS")
    print("="*120 + "\n")

    # Query the 100 oldest inspections
    inspections = FoodSafetyAgencyInspection.objects.all().order_by(
        'date_of_inspection',
        'created_at'
    )[:100]

    total_count = FoodSafetyAgencyInspection.objects.count()
    print(f"Total Inspections in Database: {total_count}")
    print(f"Showing: 100 oldest inspections\n")

    # Print table header
    print("-" * 120)
    print(f"{'#':<5} {'Client Name':<50} {'Account Code':<30} {'Inspection Date':<20}")
    print("-" * 120)

    # Display each inspection in table format
    for index, inspection in enumerate(inspections, start=1):
        client_name = (inspection.client_name or 'N/A')[:48]  # Truncate if too long
        account_code = (inspection.internal_account_code or 'N/A')[:28]
        date_str = str(inspection.date_of_inspection) if inspection.date_of_inspection else 'N/A'

        print(f"{index:<5} {client_name:<50} {account_code:<30} {date_str:<20}")

    print("-" * 120)

    # Summary
    print(f"\n{'='*120}")
    print("SUMMARY")
    print("="*120)

    # Date range
    date_range = inspections.aggregate(
        oldest=django.db.models.Min('date_of_inspection'),
        newest=django.db.models.Max('date_of_inspection')
    )
    print(f"\nDate Range:")
    print(f"  Oldest Inspection: {date_range['oldest']}")
    print(f"  Newest in this list: {date_range['newest']}")

    # Count by commodity
    print(f"\nCommodity Breakdown:")
    commodities = {}
    for insp in inspections:
        commodity = insp.commodity or 'Unknown'
        commodities[commodity] = commodities.get(commodity, 0) + 1
    for commodity, count in sorted(commodities.items(), key=lambda x: x[1], reverse=True):
        print(f"  {commodity}: {count}")

    print(f"\n{'='*120}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
