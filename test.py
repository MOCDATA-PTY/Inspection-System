"""
Test script to check egg product names retrieval and debugging
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Q, Count


def test_egg_product_names():
    """Test retrieval of egg product names from the database"""

    print("=" * 80)
    print("EGG PRODUCT NAMES DIAGNOSTIC TEST")
    print("=" * 80)

    # Test 1: Count all egg inspections
    print("\n1. COUNTING EGG INSPECTIONS")
    print("-" * 80)
    egg_inspections = FoodSafetyAgencyInspection.objects.filter(
        Q(commodity__iexact='egg') | Q(commodity__iexact='eggs')
    )
    total_eggs = egg_inspections.count()
    print(f"Total egg inspections found: {total_eggs}")

    # Test 2: Check how many have product names
    print("\n2. PRODUCT NAME STATUS")
    print("-" * 80)
    eggs_with_names = egg_inspections.filter(product_name__isnull=False).exclude(product_name='').count()
    eggs_without_names = egg_inspections.filter(Q(product_name__isnull=True) | Q(product_name='')).count()

    print(f"Egg inspections WITH product names: {eggs_with_names}")
    print(f"Egg inspections WITHOUT product names: {eggs_without_names}")
    print(f"Percentage with names: {(eggs_with_names / total_eggs * 100 if total_eggs > 0 else 0):.2f}%")

    # Test 3: Sample egg inspections with product names
    print("\n3. SAMPLE EGG INSPECTIONS WITH PRODUCT NAMES (First 10)")
    print("-" * 80)
    sample_with_names = egg_inspections.filter(
        product_name__isnull=False
    ).exclude(product_name='')[:10]

    if sample_with_names.exists():
        for i, inspection in enumerate(sample_with_names, 1):
            print(f"\n  {i}. ID: {inspection.remote_id}")
            print(f"     Client: {inspection.client_name}")
            print(f"     Date: {inspection.date_of_inspection}")
            print(f"     Commodity: {inspection.commodity}")
            print(f"     Product Name: '{inspection.product_name}'")
            print(f"     Product Class: '{inspection.product_class}'")
    else:
        print("  No egg inspections found with product names!")

    # Test 4: Sample egg inspections WITHOUT product names
    print("\n4. SAMPLE EGG INSPECTIONS WITHOUT PRODUCT NAMES (First 10)")
    print("-" * 80)
    sample_without_names = egg_inspections.filter(
        Q(product_name__isnull=True) | Q(product_name='')
    )[:10]

    if sample_without_names.exists():
        for i, inspection in enumerate(sample_without_names, 1):
            print(f"\n  {i}. ID: {inspection.remote_id}")
            print(f"     Client: {inspection.client_name}")
            print(f"     Date: {inspection.date_of_inspection}")
            print(f"     Commodity: {inspection.commodity}")
            print(f"     Product Name: '{inspection.product_name}'")
            print(f"     Product Class: '{inspection.product_class}'")
    else:
        print("  All egg inspections have product names!")

    # Test 5: Check unique product names for eggs
    print("\n5. UNIQUE EGG PRODUCT NAMES")
    print("-" * 80)
    unique_names = egg_inspections.filter(
        product_name__isnull=False
    ).exclude(product_name='').values_list('product_name', flat=True).distinct()

    if unique_names:
        print(f"Found {len(unique_names)} unique product names:")
        for name in sorted(unique_names):
            count = egg_inspections.filter(product_name=name).count()
            print(f"  - '{name}' ({count} inspections)")
    else:
        print("  No unique product names found!")

    # Test 6: Check recent egg inspections (last 30 days)
    print("\n6. RECENT EGG INSPECTIONS (Last 30 days)")
    print("-" * 80)
    from datetime import date, timedelta
    thirty_days_ago = date.today() - timedelta(days=30)

    recent_eggs = egg_inspections.filter(
        date_of_inspection__gte=thirty_days_ago
    ).order_by('-date_of_inspection')

    print(f"Recent egg inspections: {recent_eggs.count()}")

    if recent_eggs.exists():
        print("\nFirst 5 recent eggs:")
        for i, inspection in enumerate(recent_eggs[:5], 1):
            print(f"\n  {i}. ID: {inspection.remote_id}")
            print(f"     Client: {inspection.client_name}")
            print(f"     Date: {inspection.date_of_inspection}")
            print(f"     Product Name: '{inspection.product_name}'")
            print(f"     Has Name: {'YES' if inspection.product_name else 'NO'}")

    # Test 7: Check all commodities to compare
    print("\n7. PRODUCT NAME STATUS BY COMMODITY")
    print("-" * 80)
    commodities = FoodSafetyAgencyInspection.objects.values_list('commodity', flat=True).distinct()

    for commodity in sorted(set(c for c in commodities if c)):
        total = FoodSafetyAgencyInspection.objects.filter(commodity=commodity).count()
        with_names = FoodSafetyAgencyInspection.objects.filter(
            commodity=commodity,
            product_name__isnull=False
        ).exclude(product_name='').count()

        percentage = (with_names / total * 100) if total > 0 else 0
        print(f"  {commodity:15} Total: {total:5}  With Names: {with_names:5}  ({percentage:5.1f}%)")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

    return {
        'total_eggs': total_eggs,
        'with_names': eggs_with_names,
        'without_names': eggs_without_names,
    }


if __name__ == '__main__':
    try:
        results = test_egg_product_names()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
