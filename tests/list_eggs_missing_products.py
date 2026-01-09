"""
List all EGGS inspections without product names
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 80)
print("EGGS INSPECTIONS WITHOUT PRODUCT NAMES")
print("=" * 80)

# Query for EGGS inspections with missing product names
eggs_no_product = FoodSafetyAgencyInspection.objects.filter(
    commodity='EGGS',
    product_name__isnull=True
) | FoodSafetyAgencyInspection.objects.filter(
    commodity='EGGS',
    product_name=''
)

# Order by date
eggs_no_product = eggs_no_product.order_by('-date_of_inspection', 'client_name')

total_count = eggs_no_product.count()
print(f"\nTotal EGGS inspections without product names: {total_count}")
print("-" * 80)

if total_count > 0:
    print(f"\n{'ID':<15} {'Date':<12} {'Client Name':<50}")
    print("-" * 80)

    for insp in eggs_no_product:
        date_str = insp.date_of_inspection.strftime('%Y-%m-%d') if insp.date_of_inspection else 'N/A'
        client_name = (insp.client_name or 'Unknown')[:48]
        print(f"{insp.unique_inspection_id:<15} {date_str:<12} {client_name:<50}")

    # Group by client to show which clients have the most missing
    print("\n" + "=" * 80)
    print("GROUPED BY CLIENT")
    print("=" * 80)

    from django.db.models import Count

    by_client = eggs_no_product.values('client_name').annotate(
        count=Count('id')
    ).order_by('-count')

    print(f"\n{'Client Name':<50} {'Missing Count':<15}")
    print("-" * 65)

    for item in by_client:
        client = (item['client_name'] or 'Unknown')[:48]
        count = item['count']
        print(f"{client:<50} {count:<15}")

else:
    print("\n[OK] All EGGS inspections have product names!")

print("\n" + "=" * 80)
