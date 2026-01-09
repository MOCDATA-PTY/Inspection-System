"""Test that the SQL query returns both compliance and sample data correctly"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.views.data_views import FSA_INSPECTION_QUERY
import pymssql

print("=" * 100)
print("TESTING FSA_INSPECTION_QUERY - Verifying Compliance and Sample Fields")
print("=" * 100)

sql_server_config = settings.DATABASES.get('sql_server', {})

connection = pymssql.connect(
    server=sql_server_config.get('HOST'),
    port=int(sql_server_config.get('PORT', 1433)),
    user=sql_server_config.get('USER'),
    password=sql_server_config.get('PASSWORD'),
    database=sql_server_config.get('NAME'),
    timeout=30
)
cursor = connection.cursor(as_dict=True)

print(f"\n[1] Executing FSA_INSPECTION_QUERY...")
print(f"    (This is the same query the sync will use)")

cursor.execute(FSA_INSPECTION_QUERY)
results = cursor.fetchall()

print(f"\n[2] Query Results:")
print(f"    Total rows: {len(results)}")

# Check what fields are returned
if results:
    print(f"    Available fields: {list(results[0].keys())}")

    # Verify critical fields exist
    critical_fields = ['IsDirectionPresentForthisInspection', 'IsSampleTaken', 'Id', 'Commodity', 'Client']
    missing_fields = [f for f in critical_fields if f not in results[0]]

    if missing_fields:
        print(f"\n    [ERROR] Missing critical fields: {missing_fields}")
    else:
        print(f"    [OK] All critical fields present")

# Show sample data from each commodity
print(f"\n[3] Sample Data by Commodity:")
print("-" * 100)

for commodity in ['PMP', 'RAW', 'EGGS', 'POULTRY']:
    commodity_results = [r for r in results if r.get('Commodity') == commodity]

    if commodity_results:
        print(f"\n{commodity}:")

        # Count compliance status
        with_direction = sum(1 for r in commodity_results if r.get('IsDirectionPresentForthisInspection'))
        without_direction = len(commodity_results) - with_direction

        # Count sample status (only RAW and PMP have this)
        sampled = sum(1 for r in commodity_results if r.get('IsSampleTaken'))

        print(f"  Total: {len(commodity_results)}")
        print(f"  With Direction (Non-Compliant): {with_direction} ({with_direction/len(commodity_results)*100:.1f}%)")
        print(f"  Without Direction (Compliant): {without_direction} ({without_direction/len(commodity_results)*100:.1f}%)")
        if commodity in ['RAW', 'PMP']:
            print(f"  Sampled: {sampled} ({sampled/len(commodity_results)*100:.1f}%)")

        # Show first 3 examples
        print(f"\n  First 3 examples:")
        for i, r in enumerate(commodity_results[:3], 1):
            direction_status = "NON-COMPLIANT" if r.get('IsDirectionPresentForthisInspection') else "COMPLIANT"
            sample_status = "SAMPLED" if r.get('IsSampleTaken') else "NOT SAMPLED"
            client = r.get('Client', 'Unknown')[:30]

            if commodity in ['RAW', 'PMP']:
                print(f"    {i}. ID {r.get('Id')}: {client} - {direction_status}, {sample_status}")
            else:
                print(f"    {i}. ID {r.get('Id')}: {client} - {direction_status}")

# Overall statistics
print(f"\n" + "=" * 100)
print("[4] Overall Statistics:")
print("=" * 100)

total_inspections = len(results)
total_with_direction = sum(1 for r in results if r.get('IsDirectionPresentForthisInspection'))
total_without_direction = total_inspections - total_with_direction
total_sampled = sum(1 for r in results if r.get('IsSampleTaken'))

print(f"\nTotal Inspections: {total_inspections}")
print(f"Non-Compliant (Direction Present): {total_with_direction} ({total_with_direction/total_inspections*100:.1f}%)")
print(f"Compliant (No Direction): {total_without_direction} ({total_without_direction/total_inspections*100:.1f}%)")
print(f"Sampled (RAW/PMP only): {total_sampled}")

print(f"\n" + "=" * 100)
if total_with_direction > 0 and total_without_direction > 0:
    print("[SUCCESS] Query returns both compliant and non-compliant data!")
    print("The sync should work correctly now.")
else:
    print("[WARNING] All inspections have same compliance status - this seems wrong!")

print("=" * 100)

connection.close()
