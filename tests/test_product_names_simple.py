#!/usr/bin/env python3
"""
Simple test to check if product names are stored in PostgreSQL
and would display correctly in shipment_list_clean.html
"""

import os
import sys
import io
import django

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import datetime


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def check_current_state():
    """Check current state of product names in database."""
    print_section("PostgreSQL Product Names Status")

    total = FoodSafetyAgencyInspection.objects.count()
    with_products = FoodSafetyAgencyInspection.objects.exclude(
        product_name__isnull=True
    ).exclude(product_name='').count()
    without_products = total - with_products

    print(f"\nTotal inspections: {total}")
    print(f"Inspections with product names: {with_products} ({(with_products/total*100):.1f}% if total > 0 else 0)")
    print(f"Inspections without product names: {without_products} ({(without_products/total*100):.1f}% if total > 0 else 0)")

    return with_products > 0


def show_sample_with_products():
    """Show sample inspections that have product names."""
    print_section("Sample Inspections WITH Product Names")

    samples = FoodSafetyAgencyInspection.objects.exclude(
        product_name__isnull=True
    ).exclude(product_name='').order_by('-date_of_inspection')[:10]

    if not samples.exists():
        print("\nNo inspections with product names found!")
        print("\nThis means:")
        print("  1. Background sync hasn't run yet, OR")
        print("  2. SQL Server doesn't have product names for these inspections")
        return False

    print(f"\nShowing {samples.count()} most recent inspections with product names:\n")

    for i, insp in enumerate(samples, 1):
        print(f"{i}. Inspection ID: {insp.remote_id}")
        print(f"   Client: {insp.client_name}")
        print(f"   Date: {insp.date_of_inspection}")
        print(f"   Commodity: {insp.commodity}")
        print(f"   Product Name: {insp.product_name}")
        print()

    return True


def show_sample_without_products():
    """Show sample inspections that DON'T have product names."""
    print_section("Sample Inspections WITHOUT Product Names")

    samples = FoodSafetyAgencyInspection.objects.filter(
        product_name__isnull=True
    ).order_by('-date_of_inspection')[:5]

    if not samples.exists():
        samples = FoodSafetyAgencyInspection.objects.filter(
            product_name=''
        ).order_by('-date_of_inspection')[:5]

    if not samples.exists():
        print("\nAll inspections have product names!")
        return True

    print(f"\nShowing {samples.count()} inspections without product names:\n")

    for i, insp in enumerate(samples, 1):
        print(f"{i}. Inspection ID: {insp.remote_id}")
        print(f"   Client: {insp.client_name}")
        print(f"   Date: {insp.date_of_inspection}")
        print(f"   Commodity: {insp.commodity}")
        print(f"   Product Name: (None)")
        print()

    return True


def simulate_template_display():
    """Simulate how the template would display product names."""
    print_section("Template Display Simulation")

    print("\nTemplate file: main/templates/main/shipment_list_clean.html")
    print("Template logic: {% if product.product_name %}")
    print("                  <span>{{ product.product_name }}</span>")
    print("                {% else %}")
    print("                  <input type='text' placeholder='Enter product name'>")
    print("                {% endif %}")

    recent = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection')[:10]

    if not recent.exists():
        print("\nNo inspections found in database!")
        return False

    print(f"\n\nMost recent 10 inspections - How they'll appear in the table:\n")

    for i, insp in enumerate(recent, 1):
        if insp.product_name and insp.product_name.strip():
            display = f"DISPLAYS: '{insp.product_name}'"
        else:
            display = "SHOWS: [Input field for manual entry]"

        print(f"{i}. {insp.client_name} ({insp.date_of_inspection}) - {display}")

    return True


def main():
    """Run all checks."""
    print("\n" + "=" * 80)
    print("  PRODUCT NAMES TEST - PostgreSQL Database Check".center(80))
    print("=" * 80)
    print(f"\nTest time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Check current state
        has_products = check_current_state()

        # Show samples with product names
        if has_products:
            show_sample_with_products()

        # Show samples without product names
        show_sample_without_products()

        # Simulate template display
        simulate_template_display()

        # Summary
        print_section("SUMMARY")

        total = FoodSafetyAgencyInspection.objects.count()
        with_products = FoodSafetyAgencyInspection.objects.exclude(
            product_name__isnull=True
        ).exclude(product_name='').count()

        if with_products > 0:
            print(f"\nStatus: OK - {with_products} inspections have product names")
            print(f"\nThe shipment list table WILL DISPLAY product names for these {with_products} inspections.")
            print(f"The remaining {total - with_products} inspections will show input fields for manual entry.")

            if with_products < total * 0.5:
                print(f"\nNOTE: Only {(with_products/total*100):.1f}% of inspections have product names.")
                print("      This may be normal if SQL Server doesn't have product names for all inspections.")
        else:
            print("\nStatus: NO PRODUCT NAMES FOUND")
            print("\nPossible reasons:")
            print("  1. Background sync hasn't run yet")
            print("  2. SQL Server connection issues")
            print("  3. SQL Server doesn't have product names for these inspections")
            print("\nTo sync product names, run:")
            print("  python test_manual_sync.py")

        print("\n" + "=" * 80 + "\n")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
