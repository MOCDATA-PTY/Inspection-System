"""
Detailed context for EGGS inspections without product names
Shows full inspection details to help understand the data quality issue
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 100)
print("DETAILED EGGS INSPECTIONS WITHOUT PRODUCT NAMES")
print("=" * 100)

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
print("=" * 100)

if total_count > 0:
    print("\nDETAILED INSPECTION INFORMATION:")
    print("=" * 100)

    for idx, insp in enumerate(eggs_no_product, 1):
        print(f"\n[{idx}/{total_count}] Inspection: {insp.unique_inspection_id}")
        print("-" * 100)

        # Basic info
        date_str = insp.date_of_inspection.strftime('%Y-%m-%d') if insp.date_of_inspection else 'N/A'
        print(f"  Date:           {date_str}")
        print(f"  Client:         {insp.client_name or 'Unknown'}")
        print(f"  Account Code:   {insp.internal_account_code or 'N/A'}")

        # Inspector info
        print(f"  Inspector:      {insp.inspector_name or 'Unknown'} (ID: {insp.inspector_id or 'N/A'})")

        # Time info
        start_time = insp.start_of_inspection.strftime('%H:%M') if insp.start_of_inspection else 'N/A'
        end_time = insp.end_of_inspection.strftime('%H:%M') if insp.end_of_inspection else 'N/A'
        print(f"  Time:           {start_time} - {end_time}")

        # Location info
        if insp.latitude and insp.longitude:
            print(f"  GPS:            {insp.latitude}, {insp.longitude}")
        else:
            print(f"  GPS:            Not recorded")

        # Product info (what we're investigating)
        print(f"  Product Name:   [MISSING]")

        # Additional inspection details
        if insp.inspection_location_type_id:
            print(f"  Location Type:  {insp.inspection_location_type_id}")

        # Show every 50th inspection in full detail, first 10, and last 10
        if idx <= 10 or idx > total_count - 10 or idx % 50 == 0:
            if insp.is_direction_present_for_this_inspection is not None:
                print(f"  Directions:     {'Yes' if insp.is_direction_present_for_this_inspection else 'No'}")

    # Summary statistics
    print("\n" + "=" * 100)
    print("SUMMARY STATISTICS")
    print("=" * 100)

    # Group by inspector
    from django.db.models import Count

    by_inspector = eggs_no_product.values('inspector_name', 'inspector_id').annotate(
        count=Count('id')
    ).order_by('-count')

    print(f"\nBy Inspector (Top 10):")
    print(f"{'Inspector Name':<30} {'ID':<10} {'Missing Count':<15}")
    print("-" * 60)
    for item in by_inspector[:10]:
        inspector = (item['inspector_name'] or 'Unknown')[:28]
        inspector_id = str(item['inspector_id'] or 'N/A')[:8]
        count = item['count']
        print(f"{inspector:<30} {inspector_id:<10} {count:<15}")

    # Group by client
    by_client = eggs_no_product.values('client_name', 'internal_account_code').annotate(
        count=Count('id')
    ).order_by('-count')

    print(f"\nBy Client (Top 15):")
    print(f"{'Client Name':<40} {'Account Code':<15} {'Missing Count':<15}")
    print("-" * 75)
    for item in by_client[:15]:
        client = (item['client_name'] or 'Unknown')[:38]
        account = (item['internal_account_code'] or 'N/A')[:13]
        count = item['count']
        print(f"{client:<40} {account:<15} {count:<15}")

    # Date range analysis
    print(f"\nDate Range:")
    oldest = eggs_no_product.order_by('date_of_inspection').first()
    newest = eggs_no_product.order_by('-date_of_inspection').first()

    if oldest and newest:
        oldest_date = oldest.date_of_inspection.strftime('%Y-%m-%d') if oldest.date_of_inspection else 'N/A'
        newest_date = newest.date_of_inspection.strftime('%Y-%m-%d') if newest.date_of_inspection else 'N/A'
        print(f"  Oldest: {oldest_date} ({oldest.unique_inspection_id})")
        print(f"  Newest: {newest_date} ({newest.unique_inspection_id})")

    # GPS data availability
    with_gps = eggs_no_product.filter(latitude__isnull=False, longitude__isnull=False).count()
    without_gps = total_count - with_gps
    print(f"\nGPS Data Availability:")
    print(f"  With GPS:    {with_gps} ({with_gps/total_count*100:.1f}%)")
    print(f"  Without GPS: {without_gps} ({without_gps/total_count*100:.1f}%)")

    # Time data availability
    with_time = eggs_no_product.filter(
        start_of_inspection__isnull=False,
        end_of_inspection__isnull=False
    ).count()
    without_time = total_count - with_time
    print(f"\nTime Data Availability:")
    print(f"  With Time:    {with_time} ({with_time/total_count*100:.1f}%)")
    print(f"  Without Time: {without_time} ({without_time/total_count*100:.1f}%)")

else:
    print("\n[OK] All EGGS inspections have product names!")

print("\n" + "=" * 100)
print("KEY INSIGHTS")
print("=" * 100)
print(f"""
This report shows {total_count} EGGS inspections without product names.

Data Quality Issues Identified:
1. Product Name: {total_count} inspections missing this critical field
2. These inspections have all other data (client, date, inspector, etc.)
3. The product name field was likely not filled in during inspection

Recommended Actions:
1. Contact inspectors who have high counts of missing product names
2. Review data entry procedures for EGGS inspections
3. Consider making product name a required field in the mobile app
4. For "New Retailer" entries, update client names to actual business names

Impact:
- These inspections are valid but lack product identification
- This affects reporting accuracy and product tracking
- Clients cannot see which specific products were inspected
""")

print("=" * 100)
