"""
Find all inspections with client names starting with "New"
"""

import os
import django
import sys
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection


def find_new_inspections():
    """Find all inspections where client name starts with 'New'"""

    print("\n" + "="*120)
    print("INSPECTIONS WITH CLIENT NAMES STARTING WITH 'NEW'")
    print("="*120 + "\n")

    # Query for inspections with client names starting with "New"
    new_inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__istartswith='New'
    ).order_by('-date_of_inspection')

    if not new_inspections.exists():
        print("No inspections found with client names starting with 'New'")
        print("="*120 + "\n")
        return

    print(f"Found {new_inspections.count()} inspections with client names starting with 'New'\n")
    print("-"*120)

    # Group by date for better readability
    inspections_by_date = {}
    for inspection in new_inspections:
        date_key = inspection.date_of_inspection.strftime('%Y-%m-%d')
        if date_key not in inspections_by_date:
            inspections_by_date[date_key] = []
        inspections_by_date[date_key].append(inspection)

    # Display grouped results
    for date_str in sorted(inspections_by_date.keys(), reverse=True):
        inspections = inspections_by_date[date_str]
        print(f"\nDate: {date_str} ({len(inspections)} inspections)")
        print("-"*120)

        for inspection in inspections:
            print(f"  Remote ID: {inspection.remote_id}")
            print(f"  Client Name: {inspection.client_name}")
            print(f"  Account Code: {inspection.internal_account_code or 'N/A'}")
            print(f"  Commodity: {inspection.commodity}")
            print(f"  Inspector: {inspection.inspector_id}")
            print()

    # Summary statistics
    print("="*120)
    print("SUMMARY")
    print("="*120)
    print(f"Total inspections: {new_inspections.count()}")
    print(f"Date range: {new_inspections.last().date_of_inspection.strftime('%Y-%m-%d')} to {new_inspections.first().date_of_inspection.strftime('%Y-%m-%d')}")

    # Count unique client names
    unique_clients = new_inspections.values_list('client_name', flat=True).distinct()
    print(f"Unique client names: {len(unique_clients)}")
    for client in sorted(unique_clients):
        count = new_inspections.filter(client_name=client).count()
        print(f"  - {client}: {count} inspections")

    print("="*120 + "\n")

    # Generate README
    generate_readme(new_inspections, inspections_by_date)


def generate_readme(inspections, inspections_by_date):
    """Generate a simple, easy-to-read README file"""

    # Get unique client types and their account codes
    client_summary = {}
    for inspection in inspections:
        client = inspection.client_name
        account = inspection.internal_account_code or 'N/A'
        if client not in client_summary:
            client_summary[client] = {
                'count': 0,
                'account_code': account,
                'commodities': set()
            }
        client_summary[client]['count'] += 1
        client_summary[client]['commodities'].add(inspection.commodity)

    readme_content = f"""# Inspections with "New" Client Names

**Report Generated:** {datetime.now().strftime('%Y-%m-%d at %H:%M')}

---

## Quick Summary

- **Total Inspections Found:** {inspections.count()}
- **Date Range:** {inspections.last().date_of_inspection.strftime('%B %d, %Y')} to {inspections.first().date_of_inspection.strftime('%B %d, %Y')}
- **Unique Client Types:** {len(client_summary)}

---

## Client Types Found

| Client Name | Count | Account Code | Commodities |
|------------|-------|--------------|-------------|
"""

    # Sort by count (highest first)
    for client, data in sorted(client_summary.items(), key=lambda x: x[1]['count'], reverse=True):
        commodities = ', '.join(sorted(data['commodities']))
        readme_content += f"| {client} | {data['count']} | {data['account_code']} | {commodities} |\n"

    readme_content += """
---

## What This Means

These inspections have client names starting with "**New**" which indicates:

1. **Placeholder Names** - These are generic placeholder names used when the actual client couldn't be matched
2. **Missing in Database** - The account codes exist on the SQL server but aren't in the Google Sheets client database
3. **Needs Attention** - These inspections need to be matched to real client names

---

## Common Account Codes Found

"""

    # Count unique account codes
    account_codes = {}
    for inspection in inspections:
        code = inspection.internal_account_code or 'N/A'
        if code not in account_codes:
            account_codes[code] = 0
        account_codes[code] += 1

    for code, count in sorted(account_codes.items(), key=lambda x: x[1], reverse=True):
        readme_content += f"- **{code}**: {count} inspections\n"

    readme_content += """
---

## Recommended Action

Review these account codes and add them to the Google Sheets client database with their proper client names. This will ensure future inspections are automatically matched to the correct clients.

"""

    # Write to file
    readme_path = os.path.join(os.path.dirname(__file__), 'NEW_INSPECTIONS_REPORT.md')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"\n✓ README generated: {readme_path}\n")


if __name__ == "__main__":
    try:
        find_new_inspections()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
