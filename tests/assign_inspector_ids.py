#!/usr/bin/env python3
"""
Assign Inspector IDs
Helps assign inspector_id to inspections based on patterns
"""

import os
import sys
import django

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

def show_existing_inspectors():
    """Show all existing inspector IDs and names."""
    print("=" * 70)
    print("EXISTING INSPECTORS IN DATABASE")
    print("=" * 70)
    print()

    inspectors = FoodSafetyAgencyInspection.objects.exclude(
        inspector_id__isnull=True
    ).values('inspector_id', 'inspector_name').distinct().order_by('inspector_id')

    print(f"{'ID':<10} {'Name':<30}")
    print("-" * 70)

    for inspector in inspectors:
        inspector_id = inspector['inspector_id']
        inspector_name = inspector['inspector_name'] or 'No name set'
        print(f"{inspector_id:<10} {inspector_name:<30}")

    print()
    print(f"Total: {len(inspectors)} unique inspectors")
    print()

def assign_bulk_inspector_id():
    """Assign inspector_id to NULL inspections."""
    print("=" * 70)
    print("BULK ASSIGN INSPECTOR IDs")
    print("=" * 70)
    print()

    # First show existing inspectors
    show_existing_inspectors()

    # Count NULL inspector_id inspections
    null_count = FoodSafetyAgencyInspection.objects.filter(
        inspector_id__isnull=True
    ).count()

    print(f"Found {null_count} inspections with NULL inspector_id")
    print()

    if null_count == 0:
        print("No inspections to update!")
        return True

    print("Options:")
    print("  1. Assign all NULL inspections to a specific inspector_id")
    print("  2. Exit (use export script to review data first)")
    print()

    choice = input("Enter your choice (1-2): ").strip()

    if choice == '1':
        # Get inspector ID from user
        inspector_id_input = input("Enter the inspector_id to assign: ").strip()

        try:
            inspector_id = int(inspector_id_input)
        except ValueError:
            print()
            print("ERROR: Inspector ID must be a number!")
            return False

        # Get inspector name (optional)
        inspector_name = input("Enter the inspector name (or press Enter to skip): ").strip()
        if not inspector_name:
            inspector_name = None

        # Confirm
        print()
        print(f"This will update {null_count} inspections:")
        print(f"  - Set inspector_id to: {inspector_id}")
        if inspector_name:
            print(f"  - Set inspector_name to: {inspector_name}")
        print()

        confirm = input("Type 'YES' to confirm: ").strip()

        if confirm != 'YES':
            print("Cancelled.")
            return False

        # Perform update
        print()
        print("Updating inspections...")

        update_fields = {'inspector_id': inspector_id}
        if inspector_name:
            update_fields['inspector_name'] = inspector_name

        updated = FoodSafetyAgencyInspection.objects.filter(
            inspector_id__isnull=True
        ).update(**update_fields)

        print()
        print(f"SUCCESS! Updated {updated} inspections")
        print()

        return True

    elif choice == '2':
        print("Exiting...")
        return True

    else:
        print("Invalid choice!")
        return False

if __name__ == "__main__":
    try:
        success = assign_bulk_inspector_id()
        sys.exit(0 if success else 1)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"ERROR: {str(e)}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
