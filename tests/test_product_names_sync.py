#!/usr/bin/env python3
"""
Test script to verify product names are synced from SQL Server to PostgreSQL
and displayed correctly in shipment_list_clean.html

This script:
1. Runs a background sync to fetch data from SQL Server
2. Verifies product names are stored in PostgreSQL FoodSafetyAgencyInspection model
3. Checks that the data would display correctly in the template
"""

import os
import sys
import io
import django
from datetime import datetime, timedelta

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection
from main.services.scheduled_sync_service import scheduled_sync_service


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_background_sync():
    """Test the background sync service."""
    print_section("STEP 1: Testing Background Sync Service")

    print("\n📊 Current PostgreSQL database state BEFORE sync:")
    total_before = FoodSafetyAgencyInspection.objects.count()
    with_products_before = FoodSafetyAgencyInspection.objects.exclude(
        product_name__isnull=True
    ).exclude(product_name='').count()

    print(f"   Total inspections: {total_before}")
    print(f"   Inspections with product names: {with_products_before}")
    print(f"   Inspections without product names: {total_before - with_products_before}")

    # Run the sync
    print("\n🔄 Running SQL Server sync...")
    print("   This will fetch inspection data and product names from SQL Server...")
    success, message = scheduled_sync_service.run_manual_sync('sql_server')

    if success:
        print(f"   ✅ {message}")
    else:
        print(f"   ❌ {message}")
        return False

    return True


def verify_postgresql_storage():
    """Verify product names are stored in PostgreSQL."""
    print_section("STEP 2: Verifying PostgreSQL Storage")

    total = FoodSafetyAgencyInspection.objects.count()
    with_products = FoodSafetyAgencyInspection.objects.exclude(
        product_name__isnull=True
    ).exclude(product_name='').count()
    without_products = total - with_products

    print(f"\n📊 PostgreSQL database state AFTER sync:")
    print(f"   Total inspections: {total}")
    print(f"   Inspections with product names: {with_products} ({(with_products/total*100):.1f}%)")
    print(f"   Inspections without product names: {without_products} ({(without_products/total*100):.1f}%)")

    # Show some sample inspections with product names
    print("\n📋 Sample inspections with product names:")
    samples = FoodSafetyAgencyInspection.objects.exclude(
        product_name__isnull=True
    ).exclude(product_name='').order_by('-date_of_inspection')[:10]

    if samples.exists():
        for i, inspection in enumerate(samples, 1):
            print(f"\n   {i}. Inspection ID: {inspection.remote_id}")
            print(f"      Client: {inspection.client_name}")
            print(f"      Date: {inspection.date_of_inspection}")
            print(f"      Commodity: {inspection.commodity}")
            print(f"      Product Name: {inspection.product_name}")
            print(f"      Inspector: {inspection.inspector_name}")
    else:
        print("   ⚠️ No inspections with product names found!")
        return False

    # Show some inspections without product names
    print("\n📋 Sample inspections WITHOUT product names:")
    samples_without = FoodSafetyAgencyInspection.objects.filter(
        product_name__isnull=True
    ).order_by('-date_of_inspection')[:5]

    if not samples_without.exists():
        samples_without = FoodSafetyAgencyInspection.objects.filter(
            product_name=''
        ).order_by('-date_of_inspection')[:5]

    if samples_without.exists():
        for i, inspection in enumerate(samples_without, 1):
            print(f"\n   {i}. Inspection ID: {inspection.remote_id}")
            print(f"      Client: {inspection.client_name}")
            print(f"      Date: {inspection.date_of_inspection}")
            print(f"      Commodity: {inspection.commodity}")
            print(f"      Product Name: {inspection.product_name or '(None)'}")

    return with_products > 0


def verify_template_display():
    """Verify how data would be displayed in the template."""
    print_section("STEP 3: Verifying Template Display Logic")

    print("\n🖼️ Simulating template rendering logic...")
    print("   Template file: main/templates/main/shipment_list_clean.html")
    print("   Template checks for: {{ product.product_name|default:'' }}")

    # Get recent inspections
    recent_inspections = FoodSafetyAgencyInspection.objects.order_by(
        '-date_of_inspection'
    )[:20]

    with_product_names = []
    without_product_names = []

    for insp in recent_inspections:
        if insp.product_name and insp.product_name.strip():
            with_product_names.append(insp)
        else:
            without_product_names.append(insp)

    print(f"\n📊 Recent 20 inspections:")
    print(f"   Will display product name: {len(with_product_names)}")
    print(f"   Will show input field (no product name): {len(without_product_names)}")

    if with_product_names:
        print(f"\n✅ Template will DISPLAY product names for these inspections:")
        for insp in with_product_names[:5]:
            print(f"   - {insp.client_name} on {insp.date_of_inspection}: '{insp.product_name}'")

    if without_product_names:
        print(f"\n⚠️ Template will show INPUT FIELD for these inspections:")
        for insp in without_product_names[:5]:
            print(f"   - {insp.client_name} on {insp.date_of_inspection}: (no product name)")

    return len(with_product_names) > 0


def test_specific_inspection(inspection_id=None):
    """Test a specific inspection by ID."""
    print_section("STEP 4: Testing Specific Inspection")

    if inspection_id:
        print(f"\n🔍 Looking for inspection with remote_id={inspection_id}...")
        try:
            inspection = FoodSafetyAgencyInspection.objects.get(remote_id=inspection_id)
        except FoodSafetyAgencyInspection.DoesNotExist:
            print(f"   ❌ Inspection with remote_id={inspection_id} not found!")
            return False
    else:
        # Get the most recent inspection with a product name
        inspection = FoodSafetyAgencyInspection.objects.exclude(
            product_name__isnull=True
        ).exclude(product_name='').order_by('-date_of_inspection').first()

        if not inspection:
            print("   ❌ No inspections with product names found!")
            return False

    print(f"\n📄 Inspection Details:")
    print(f"   Remote ID: {inspection.remote_id}")
    print(f"   Client: {inspection.client_name}")
    print(f"   Date: {inspection.date_of_inspection}")
    print(f"   Commodity: {inspection.commodity}")
    print(f"   Inspector: {inspection.inspector_name}")
    print(f"   Product Name: {inspection.product_name or '(None)'}")
    print(f"   Last Synced: {inspection.last_synced}")

    # Check if it would display in template
    if inspection.product_name and inspection.product_name.strip():
        print(f"\n   ✅ This inspection WILL DISPLAY the product name in the template")
        print(f"   Template output: <span class='product-name-text'>{inspection.product_name}</span>")
    else:
        print(f"\n   ⚠️ This inspection will show an INPUT FIELD (no product name)")
        print(f"   Template output: <input type='text' placeholder='Enter product name'>")

    return True


def run_all_tests():
    """Run all tests in sequence."""
    print("\n")
    print("=" * 80)
    print("  PRODUCT NAME SYNC TEST - SQL Server to PostgreSQL".center(80))
    print("=" * 80)

    print(f"\n⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗄️ PostgreSQL Database: {settings.DATABASES['default']['NAME']}")
    print(f"🗄️ SQL Server: {settings.DATABASES.get('sql_server', {}).get('HOST', 'Not configured')}")

    # Run tests
    results = {
        'sync': False,
        'storage': False,
        'template': False,
        'specific': False
    }

    try:
        # Test 1: Background sync
        results['sync'] = test_background_sync()

        # Test 2: Verify PostgreSQL storage
        if results['sync']:
            results['storage'] = verify_postgresql_storage()
        else:
            print("\n⚠️ Skipping storage verification due to sync failure")

        # Test 3: Verify template display
        if results['storage']:
            results['template'] = verify_template_display()
        else:
            print("\n⚠️ Skipping template verification due to storage issues")

        # Test 4: Test specific inspection
        results['specific'] = test_specific_inspection()

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

    # Final summary
    print_section("FINAL SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n📊 Test Results: {passed}/{total} passed")
    print(f"\n   {'✅' if results['sync'] else '❌'} Background Sync: {'PASSED' if results['sync'] else 'FAILED'}")
    print(f"   {'✅' if results['storage'] else '❌'} PostgreSQL Storage: {'PASSED' if results['storage'] else 'FAILED'}")
    print(f"   {'✅' if results['template'] else '❌'} Template Display: {'PASSED' if results['template'] else 'FAILED'}")
    print(f"   {'✅' if results['specific'] else '❌'} Specific Inspection: {'PASSED' if results['specific'] else 'FAILED'}")

    if all(results.values()):
        print("\n" + "🎉" * 40)
        print("   ALL TESTS PASSED! Product names are syncing correctly!")
        print("🎉" * 40)
    else:
        print("\n⚠️ Some tests failed. Review the output above for details.")

    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    run_all_tests()
