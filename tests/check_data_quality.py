"""
Data Quality Monitoring Script
Checks for missing or incomplete data in inspections
Run this daily to monitor data quality
"""
import os
import django
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, Notification
from django.db.models import Q

def check_missing_product_names():
    """Find inspections with missing product names."""

    # Check last 7 days
    week_ago = datetime.now().date() - timedelta(days=7)

    missing = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=week_ago,
        product_name__in=['', None]
    ).order_by('-date_of_inspection')

    return missing

def check_missing_client_names():
    """Find inspections with missing client names."""

    week_ago = datetime.now().date() - timedelta(days=7)

    missing = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=week_ago,
        client_name__in=['', None]
    ).order_by('-date_of_inspection')

    return missing

def check_missing_inspector_names():
    """Find inspections with missing inspector names."""

    week_ago = datetime.now().date() - timedelta(days=7)

    missing = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=week_ago,
        inspector_name__in=['', None]
    ).order_by('-date_of_inspection')

    return missing

def main():
    print("=" * 80)
    print("DATA QUALITY MONITORING REPORT")
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    issues_found = False

    # Check missing product names
    print("1. Checking for missing product names (last 7 days)...")
    missing_products = check_missing_product_names()

    if missing_products.exists():
        issues_found = True
        print(f"   [WARNING] {missing_products.count()} inspections missing product names")

        # Show details
        for insp in missing_products[:5]:  # Show first 5
            print(f"      - {insp.unique_inspection_id}: {insp.inspector_name} | {insp.client_name} | {insp.date_of_inspection}")

        if missing_products.count() > 5:
            print(f"      ... and {missing_products.count() - 5} more")

        # Create notification
        try:
            Notification.notify_super_admins(
                title="Data Quality Alert: Missing Product Names",
                message=f"{missing_products.count()} inspections from the past 7 days are missing product names. Please review and update.",
                notification_type='warning',
                priority='medium',
                action_url='/admin/main/foodsafetyagencyinspection/?product_name__exact='
            )
            print("      [INFO] Admin notification created")
        except Exception as e:
            print(f"      [ERROR] Could not create notification: {e}")
    else:
        print("   [OK] All recent inspections have product names")

    print()

    # Check missing client names
    print("2. Checking for missing client names (last 7 days)...")
    missing_clients = check_missing_client_names()

    if missing_clients.exists():
        issues_found = True
        print(f"   [WARNING] {missing_clients.count()} inspections missing client names")

        for insp in missing_clients[:5]:
            print(f"      - {insp.unique_inspection_id}: {insp.inspector_name} | {insp.date_of_inspection}")

        if missing_clients.count() > 5:
            print(f"      ... and {missing_clients.count() - 5} more")

        # Create notification
        try:
            Notification.notify_super_admins(
                title="Data Quality Alert: Missing Client Names",
                message=f"{missing_clients.count()} inspections from the past 7 days are missing client names.",
                notification_type='error',
                priority='high',
                action_url='/admin/main/foodsafetyagencyinspection/?client_name__exact='
            )
            print("      [INFO] Admin notification created")
        except Exception as e:
            print(f"      [ERROR] Could not create notification: {e}")
    else:
        print("   [OK] All recent inspections have client names")

    print()

    # Check missing inspector names
    print("3. Checking for missing inspector names (last 7 days)...")
    missing_inspectors = check_missing_inspector_names()

    if missing_inspectors.exists():
        issues_found = True
        print(f"   [CRITICAL] {missing_inspectors.count()} inspections missing inspector names")

        for insp in missing_inspectors[:5]:
            print(f"      - {insp.unique_inspection_id}: {insp.client_name} | {insp.date_of_inspection}")

        if missing_inspectors.count() > 5:
            print(f"      ... and {missing_inspectors.count() - 5} more")

        # Create notification
        try:
            Notification.notify_super_admins(
                title="Data Quality Alert: Missing Inspector Names",
                message=f"{missing_inspectors.count()} inspections from the past 7 days are missing inspector names!",
                notification_type='error',
                priority='critical',
                action_url='/admin/main/foodsafetyagencyinspection/?inspector_name__exact='
            )
            print("      [INFO] Admin notification created")
        except Exception as e:
            print(f"      [ERROR] Could not create notification: {e}")
    else:
        print("   [OK] All recent inspections have inspector names")

    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if issues_found:
        total_issues = (
            missing_products.count() +
            missing_clients.count() +
            missing_inspectors.count()
        )
        print(f"\n[WARNING] {total_issues} data quality issues found in the last 7 days")
        print("\nActions required:")
        print("  1. Review missing data in Django admin panel")
        print("  2. Contact inspectors to fill in missing information")
        print("  3. Update mobile app validation to prevent future issues")
        print("\nFor detailed list, run: python find_missing_product_names.py")
    else:
        print("\n[OK] No data quality issues found!")
        print("All inspections from the last 7 days have complete data")

    print()
    print("=" * 80)
    print(f"Report completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Data quality check failed: {e}")
        import traceback
        traceback.print_exc()
