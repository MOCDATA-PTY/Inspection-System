"""
Find all inspections with missing product names
This helps identify the scope of the data quality issue
"""
import os
import django
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Q, Count

print("=" * 80)
print("FINDING INSPECTIONS WITH MISSING PRODUCT NAMES")
print("=" * 80)
print()

# Query for inspections with missing product names
missing = FoodSafetyAgencyInspection.objects.filter(
    Q(product_name__isnull=True) | Q(product_name='')
).order_by('-date_of_inspection')

total_inspections = FoodSafetyAgencyInspection.objects.count()
missing_count = missing.count()
percentage = (missing_count / total_inspections * 100) if total_inspections > 0 else 0

print(f"Total Inspections: {total_inspections}")
print(f"Missing Product Names: {missing_count} ({percentage:.2f}%)")
print()

if missing_count == 0:
    print("[OK] All inspections have product names!")
else:
    print(f"[WARNING] {missing_count} inspections are missing product names")
    print()

    # Breakdown by commodity
    print("Breakdown by Commodity:")
    print("-" * 80)

    commodity_breakdown = missing.values('commodity').annotate(
        count=Count('id')
    ).order_by('-count')

    for item in commodity_breakdown:
        commodity = item['commodity'] or 'Unknown'
        count = item['count']
        print(f"  {commodity:15s}: {count:5d} inspections")

    print()

    # Breakdown by inspector
    print("Breakdown by Inspector (Top 10):")
    print("-" * 80)

    inspector_breakdown = missing.values('inspector_name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    for item in inspector_breakdown:
        inspector = item['inspector_name'] or 'Unknown'
        count = item['count']
        print(f"  {inspector:30s}: {count:5d} inspections")

    print()

    # Recent missing (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_missing = missing.filter(date_of_inspection__gte=thirty_days_ago)

    print(f"Recent (Last 30 Days): {recent_missing.count()} inspections")
    print("-" * 80)

    if recent_missing.count() > 0:
        print("\nMost Recent 20 Inspections Missing Product Names:")
        for i, insp in enumerate(recent_missing[:20], 1):
            print(f"{i:2d}. {insp.unique_inspection_id:15s} | {insp.date_of_inspection} | {insp.inspector_name:20s} | {insp.client_name}")

    print()

    # Export to file option
    print("=" * 80)
    print("EXPORT OPTIONS")
    print("=" * 80)

    response = input("\nExport full list to CSV? (yes/no): ").strip().lower()

    if response in ['yes', 'y']:
        import csv
        from datetime import datetime

        filename = f"missing_product_names_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Header
            writer.writerow([
                'Inspection ID',
                'Unique ID',
                'Commodity',
                'Date',
                'Inspector',
                'Client Name',
                'Account Code',
                'Product Name',
                'Sample Taken',
                'Created At'
            ])

            # Data
            for insp in missing:
                writer.writerow([
                    insp.id,
                    insp.unique_inspection_id,
                    insp.commodity,
                    insp.date_of_inspection,
                    insp.inspector_name,
                    insp.client_name,
                    insp.internal_account_code,
                    insp.product_name or '[EMPTY]',
                    insp.is_sample_taken,
                    insp.created_at
                ])

        print(f"\n[OK] Exported {missing_count} records to: {filename}")
    else:
        print("\n[INFO] Export cancelled")

print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
