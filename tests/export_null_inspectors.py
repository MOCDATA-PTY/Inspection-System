#!/usr/bin/env python3
"""
Export NULL Inspector ID Inspections
Creates an Excel file with all inspections that have NULL inspector_id
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

def export_null_inspectors():
    """Export inspections with NULL inspector_id to Excel."""
    print("=" * 70)
    print("EXPORT NULL INSPECTOR ID INSPECTIONS")
    print("=" * 70)
    print()

    # Query for NULL inspector_id inspections
    null_inspections = FoodSafetyAgencyInspection.objects.filter(
        inspector_id__isnull=True
    ).values(
        'id',
        'inspector_id',
        'inspector_name',
        'date_of_inspection',
        'client_name',
        'commodity',
        'approved_status',
        'hours',
        'km_traveled'
    ).order_by('-date_of_inspection')

    print(f"Found {len(null_inspections)} inspections with NULL inspector_id")
    print()

    if len(null_inspections) == 0:
        print("No inspections with NULL inspector_id found!")
        return True

    # Convert to DataFrame
    df = pd.DataFrame(list(null_inspections))

    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'null_inspector_inspections_{timestamp}.xlsx'

    # Export to Excel
    df.to_excel(filename, index=False, engine='openpyxl')

    print(f"SUCCESS! Data exported to: {filename}")
    print()
    print("Column breakdown:")
    print(f"  - id: Inspection ID")
    print(f"  - inspector_id: Currently NULL")
    print(f"  - inspector_name: Current name (if any)")
    print(f"  - date_of_inspection: When inspection occurred")
    print(f"  - client_name: Client that was inspected")
    print(f"  - commodity: What was inspected")
    print(f"  - approved_status: APPROVED or PENDING")
    print(f"  - hours: Hours worked")
    print(f"  - km_traveled: Distance traveled")
    print()
    print("Next steps:")
    print("  1. Open the Excel file")
    print("  2. Review each inspection")
    print("  3. Determine which inspector should be assigned")
    print("  4. Update the inspector_id in the database")
    print()

    return True

if __name__ == "__main__":
    try:
        success = export_null_inspectors()
        sys.exit(0 if success else 1)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"ERROR: {str(e)}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
