"""
Find inspection with client name containing '-' on November 14, 2025
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection


def find_inspection():
    """Find inspection on Nov 14, 2025 with client name containing '-'"""

    print("\n" + "="*100)
    print("SEARCHING FOR INSPECTION ON NOVEMBER 14, 2025 WITH CLIENT NAME CONTAINING '-'")
    print("="*100 + "\n")

    # Search for inspections on Nov 14, 2025
    inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection="2025-11-14",
        client_name__icontains="-"
    )

    print(f"Found {inspections.count()} inspection(s)\n")

    if not inspections.exists():
        # Try broader search
        all_nov_14 = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection="2025-11-14"
        )
        print(f"Total inspections on Nov 14: {all_nov_14.count()}")
        print("\nShowing all inspections on Nov 14:\n")
        for idx, inspection in enumerate(all_nov_14[:20], 1):
            print(f"{idx}. Client: '{inspection.client_name}' | Remote ID: {inspection.remote_id}")
        return

    for idx, inspection in enumerate(inspections, 1):
        print(f"\n{'-'*100}")
        print(f"INSPECTION #{idx}")
        print(f"{'-'*100}")
        print(f"Remote ID: {inspection.remote_id}")
        print(f"Client Name: '{inspection.client_name}'")
        print(f"Date: {inspection.date_of_inspection}")
        print(f"Commodity: {inspection.commodity}")
        print(f"Inspector: {inspection.inspector_name}")
        print(f"Lab: {inspection.lab}")
        print(f"Sample Taken: {inspection.is_sample_taken}")

    print("\n" + "="*100 + "\n")


if __name__ == "__main__":
    try:
        find_inspection()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
