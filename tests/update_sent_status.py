import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import datetime

# Find the inspection for Hume International
# with inspection date 17/10/2025
try:
    # Convert the date string to a date object
    inspection_date = datetime.strptime('17/10/2025', '%d/%m/%Y').date()

    # Find all inspections for Hume International on that date
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains='Hume',
        date_of_inspection=inspection_date
    )

    if not inspections:
        print("No inspections found for Hume International on 17/10/2025")
    else:
        print(f"Found {inspections.count()} inspection(s):")
        for inspection in inspections:
            print(f"\n  Client: {inspection.client_name}")
            print(f"  Inspector: {inspection.inspector_name}")
            print(f"  Inspection Date: {inspection.date_of_inspection}")
            print(f"  Commodity: {inspection.commodity}")
            print(f"  Current is_sent: {inspection.is_sent}")
            print(f"  Current sent_date: {inspection.sent_date}")

            # Update the sent status
            inspection.is_sent = False
            inspection.sent_date = None
            inspection.sent_by = None
            inspection.save()

            print(f"  >>> Updated successfully!")
            print(f"  New is_sent: {inspection.is_sent}")
            print(f"  New sent_date: {inspection.sent_date}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
