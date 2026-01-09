#!/usr/bin/env python3
"""
Quick test to verify manual sync is working on production server
Run this on the server after deployment
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.scheduled_sync_service import scheduled_sync_service
from main.models import FoodSafetyAgencyInspection
from datetime import datetime


def test_sync():
    """Test the sync functionality."""

    print("\n" + "=" * 80)
    print("  MANUAL SYNC TEST - Production Server")
    print("=" * 80)
    print(f"\nTest time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check before sync
    print("BEFORE SYNC:")
    total_before = FoodSafetyAgencyInspection.objects.count()
    with_products_before = FoodSafetyAgencyInspection.objects.exclude(
        product_name__isnull=True
    ).exclude(product_name='').count()

    print(f"  Total inspections: {total_before}")
    print(f"  With product names: {with_products_before} ({(with_products_before/total_before*100):.1f}%)")

    # Run sync
    print("\n" + "-" * 80)
    print("RUNNING SQL SERVER SYNC...")
    print("-" * 80 + "\n")

    try:
        success, message = scheduled_sync_service.run_manual_sync('sql_server')

        if success:
            print(f"\n✅ SUCCESS: {message}")
        else:
            print(f"\n❌ FAILED: {message}")
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Check after sync
    print("\n" + "-" * 80)
    print("AFTER SYNC:")
    print("-" * 80 + "\n")

    total_after = FoodSafetyAgencyInspection.objects.count()
    with_products_after = FoodSafetyAgencyInspection.objects.exclude(
        product_name__isnull=True
    ).exclude(product_name='').count()

    print(f"  Total inspections: {total_after}")
    print(f"  With product names: {with_products_after} ({(with_products_after/total_after*100):.1f}%)")

    # Show changes
    new_inspections = total_after - total_before
    new_product_names = with_products_after - with_products_before

    print("\nCHANGES:")
    print(f"  New inspections added: {new_inspections}")
    print(f"  New product names added: {new_product_names}")

    # Show recent inspections with product names
    print("\n" + "-" * 80)
    print("RECENT INSPECTIONS WITH PRODUCT NAMES:")
    print("-" * 80 + "\n")

    recent = FoodSafetyAgencyInspection.objects.exclude(
        product_name__isnull=True
    ).exclude(product_name='').order_by('-date_of_inspection')[:5]

    if recent.exists():
        for i, insp in enumerate(recent, 1):
            print(f"{i}. {insp.client_name} ({insp.date_of_inspection})")
            print(f"   Commodity: {insp.commodity}")
            print(f"   Product: {insp.product_name}")
            print()
    else:
        print("  No inspections with product names found!")

    print("=" * 80)
    print("TEST COMPLETED")
    print("=" * 80 + "\n")

    return True


if __name__ == "__main__":
    try:
        success = test_sync()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
