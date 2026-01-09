"""
Check what commodity values are in recent inspections
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import date
from collections import Counter

def check_inspection_commodities():
    # Get recent November inspections
    start_date = date(2025, 11, 1)
    end_date = date(2025, 11, 19)

    inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=start_date,
        date_of_inspection__lte=end_date
    ).exclude(commodity__isnull=True)

    commodities = Counter()

    for inspection in inspections:
        commodity = str(inspection.commodity).strip()
        commodities[commodity] += 1

    print("Commodity values in November inspections:")
    print("="*50)
    for commodity, count in commodities.most_common():
        print(f"{commodity:20} : {count:4} inspections")

    print(f"\n{'='*50}")
    print(f"Total: {sum(commodities.values())} inspections")

    print("\n\nFile commodities (from Drive):")
    print("="*50)
    print("Poultry")
    print("Raw")
    print("Egg")
    print("PMP")

    print("\n\nCommodity mapping needed:")
    print("="*50)
    for commodity in sorted(commodities.keys()):
        commodity_lower = commodity.lower()
        if commodity_lower == "eggs":
            commodity_lower = "egg"
        print(f"{commodity:20} -> {commodity_lower}")

if __name__ == "__main__":
    check_inspection_commodities()
