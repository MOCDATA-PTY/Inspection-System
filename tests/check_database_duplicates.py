"""Check for duplicate inspection records in database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Count

print("=" * 100)
print("CHECKING FOR DUPLICATE INSPECTION RECORDS")
print("=" * 100)

# Find potential duplicates (same client, date, inspector, product, commodity)
duplicates = FoodSafetyAgencyInspection.objects.values(
    'client_name',
    'date_of_inspection',
    'inspector_name',
    'product_name',
    'commodity'
).annotate(
    count=Count('id')
).filter(count__gt=1).order_by('-count')

print(f"\nFound {len(duplicates)} groups of potential duplicates\n")

if len(duplicates) > 0:
    for dup in duplicates[:10]:  # Show first 10
        print("=" * 100)
        print(f"DUPLICATE GROUP ({dup['count']} records):")
        print(f"  Client: {dup['client_name']}")
        print(f"  Date: {dup['date_of_inspection']}")
        print(f"  Inspector: {dup['inspector_name']}")
        print(f"  Product: {dup['product_name']}")
        print(f"  Commodity: {dup['commodity']}")

        # Get the actual records
        records = FoodSafetyAgencyInspection.objects.filter(
            client_name=dup['client_name'],
            date_of_inspection=dup['date_of_inspection'],
            inspector_name=dup['inspector_name'],
            product_name=dup['product_name'],
            commodity=dup['commodity']
        )

        print(f"\n  Actual records:")
        for rec in records:
            print(f"    ID: {rec.id}, RemoteID: {rec.remote_id}, Hours: {rec.hours}, KM: {rec.km_traveled}")
            print(f"      Fat: {rec.fat}, Protein: {rec.protein}, Sampled: {rec.is_sample_taken}")

else:
    print("No duplicate records found!")
    print("\nDuplicates in export must be from logic, not database.")

print("\n" + "=" * 100)
