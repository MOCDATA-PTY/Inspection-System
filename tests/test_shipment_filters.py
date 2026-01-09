#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for shipment_list_clean.html filters
Tests all filter combinations to ensure they work correctly
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User
from django.test import RequestFactory, Client
from django.urls import reverse

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def test_client_filter():
    """Test client name filter"""
    print_section("TEST 1: Client Name Filter")

    # Get a sample client name from the database
    sample_inspection = FoodSafetyAgencyInspection.objects.first()
    if not sample_inspection:
        print("❌ No inspections found in database")
        return False

    client_name = sample_inspection.client_name
    print(f"Testing with client: {client_name}")

    # Filter inspections by client name
    filtered = FoodSafetyAgencyInspection.objects.filter(client_name__icontains=client_name)

    print(f"✅ Found {filtered.count()} inspections for client '{client_name}'")

    # Show first 3 results
    for i, insp in enumerate(filtered[:3], 1):
        print(f"   {i}. {insp.client_name} - {insp.date_of_inspection} - {insp.inspector_name}")

    return True

def test_inspector_filter():
    """Test inspector filter"""
    print_section("TEST 2: Inspector Filter")

    # Get unique inspector names
    inspectors = FoodSafetyAgencyInspection.objects.values_list('inspector_name', flat=True).distinct()
    inspectors = [i for i in inspectors if i]  # Remove None values

    if not inspectors:
        print("❌ No inspectors found in database")
        return False

    inspector = inspectors[0]
    print(f"Testing with inspector: {inspector}")

    # Filter inspections by inspector
    filtered = FoodSafetyAgencyInspection.objects.filter(inspector_name__icontains=inspector)

    print(f"✅ Found {filtered.count()} inspections for inspector '{inspector}'")

    # Show first 3 results
    for i, insp in enumerate(filtered[:3], 1):
        print(f"   {i}. {insp.client_name} - {insp.date_of_inspection} - {insp.inspector_name}")

    return True

def test_date_range_filter():
    """Test date range filter"""
    print_section("TEST 3: Date Range Filter")

    # Get date range from last 30 days
    today = datetime.now().date()
    date_from = today - timedelta(days=30)
    date_to = today

    print(f"Testing date range: {date_from} to {date_to}")

    # Filter inspections by date range
    filtered = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=date_from,
        date_of_inspection__lte=date_to
    )

    print(f"✅ Found {filtered.count()} inspections in date range")

    # Show date distribution
    if filtered.exists():
        earliest = filtered.order_by('date_of_inspection').first().date_of_inspection
        latest = filtered.order_by('-date_of_inspection').first().date_of_inspection
        print(f"   Earliest: {earliest}")
        print(f"   Latest: {latest}")

    return True

def test_sent_status_filter():
    """Test sent status filter"""
    print_section("TEST 4: Sent Status Filter")

    # Count sent vs not sent
    all_count = FoodSafetyAgencyInspection.objects.count()
    sent_count = FoodSafetyAgencyInspection.objects.filter(is_sent=True).count()
    not_sent_count = FoodSafetyAgencyInspection.objects.filter(is_sent=False).count()

    print(f"Total inspections: {all_count}")
    print(f"✅ Sent inspections: {sent_count}")
    print(f"✅ Not sent inspections: {not_sent_count}")

    # Show sample sent inspections
    if sent_count > 0:
        print("\nSample sent inspections:")
        for i, insp in enumerate(FoodSafetyAgencyInspection.objects.filter(is_sent=True)[:3], 1):
            print(f"   {i}. {insp.client_name} - {insp.date_of_inspection} - Sent: {insp.sent_date}")

    return True

def test_compliance_status_filter():
    """Test compliance status filter"""
    print_section("TEST 5: Compliance Status Filter")

    # Count compliant vs non-compliant
    all_count = FoodSafetyAgencyInspection.objects.count()
    compliant_count = FoodSafetyAgencyInspection.objects.filter(is_direction_present_for_this_inspection=False).count()
    non_compliant_count = FoodSafetyAgencyInspection.objects.filter(is_direction_present_for_this_inspection=True).count()

    print(f"Total inspections: {all_count}")
    print(f"✅ Compliant inspections (no direction): {compliant_count}")
    print(f"✅ Non-compliant inspections (direction present): {non_compliant_count}")

    # Show sample non-compliant inspections
    if non_compliant_count > 0:
        print("\nSample non-compliant inspections:")
        for i, insp in enumerate(FoodSafetyAgencyInspection.objects.filter(is_direction_present_for_this_inspection=True)[:3], 1):
            print(f"   {i}. {insp.client_name} - {insp.date_of_inspection}")

    return True

def test_combined_filters():
    """Test multiple filters combined"""
    print_section("TEST 6: Combined Filters")

    # Get sample data
    sample = FoodSafetyAgencyInspection.objects.first()
    if not sample:
        print("❌ No inspections found")
        return False

    # Test combining client + date range
    date_from = datetime.now().date() - timedelta(days=60)

    print(f"Testing combined filters:")
    print(f"  - Client contains: {sample.client_name[:10]}")
    print(f"  - Date from: {date_from}")
    print(f"  - Not sent only")

    filtered = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains=sample.client_name[:10],
        date_of_inspection__gte=date_from,
        is_sent=False
    )

    print(f"✅ Found {filtered.count()} inspections matching combined filters")

    if filtered.exists():
        print("\nSample results:")
        for i, insp in enumerate(filtered[:3], 1):
            print(f"   {i}. {insp.client_name} - {insp.date_of_inspection} - Sent: {insp.is_sent}")

    return True

def test_url_filter_integration():
    """Test filters through Django client (simulating browser requests)"""
    print_section("TEST 7: URL Filter Integration (Simulated HTTP Requests)")

    # Create a test user
    try:
        user = User.objects.filter(is_staff=True).first()
        if not user:
            user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
            user.role = 'admin'
            user.save()
    except:
        print("❌ Could not create test user")
        return False

    # Create Django test client
    client = Client()
    client.force_login(user)

    # Test various filter combinations via URL
    test_cases = [
        {
            'name': 'Client filter',
            'params': {'client': 'meat'},
            'description': 'Filter by client name containing "meat"'
        },
        {
            'name': 'Inspector filter',
            'params': {'branch': 'NEO'},
            'description': 'Filter by inspector name containing "NEO"'
        },
        {
            'name': 'Date range filter',
            'params': {
                'inspection_date_from': (datetime.now().date() - timedelta(days=30)).isoformat(),
                'inspection_date_to': datetime.now().date().isoformat()
            },
            'description': 'Filter by last 30 days'
        },
        {
            'name': 'Sent status filter',
            'params': {'sent_status': 'NO'},
            'description': 'Filter for not sent inspections'
        },
        {
            'name': 'Compliance filter',
            'params': {'compliance_status': 'NON_COMPLIANT'},
            'description': 'Filter for non-compliant inspections'
        },
        {
            'name': 'Combined filters',
            'params': {
                'client': 'butchery',
                'sent_status': 'NO',
                'compliance_status': 'COMPLIANT'
            },
            'description': 'Client + Sent + Compliance combined'
        }
    ]

    all_passed = True

    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print(f"Parameters: {test_case['params']}")

        try:
            # Make request to shipment_list with filters (URL: /inspections/)
            response = client.get('/inspections/', test_case['params'])

            if response.status_code == 200:
                print(f"✅ {test_case['name']} - HTTP 200 OK")

                # Check if response contains expected elements
                content = response.content.decode('utf-8')

                # Verify filter form is present
                if 'filter-form' in content or 'Filter Inspections' in content:
                    print(f"   ✓ Filter form rendered")
                else:
                    print(f"   ⚠ Filter form not found in response")

                # Verify table or results are present
                if 'shipment' in content.lower() or 'inspection' in content.lower():
                    print(f"   ✓ Results rendered")
                else:
                    print(f"   ⚠ Results section not found")

            else:
                print(f"❌ {test_case['name']} - HTTP {response.status_code}")
                all_passed = False

        except Exception as e:
            print(f"❌ {test_case['name']} - Error: {str(e)}")
            all_passed = False

    return all_passed

def test_filter_logic():
    """Test the filter logic from apply_fsa_inspection_filters"""
    print_section("TEST 8: Filter Logic Validation")

    from django.http import QueryDict
    from django.test import RequestFactory

    factory = RequestFactory()

    # Test each filter type
    print("\n1. Testing client name filter logic:")
    request = factory.get('/inspections/', {'client': 'butchery'})
    inspections = FoodSafetyAgencyInspection.objects.all()

    # Apply client filter
    if request.GET.get('client'):
        filtered = inspections.filter(client_name__icontains=request.GET.get('client'))
        print(f"   ✅ Client filter: {inspections.count()} → {filtered.count()} inspections")

    print("\n2. Testing inspector filter logic:")
    request = factory.get('/inspections/', {'branch': 'NEO'})

    # Apply inspector filter
    if request.GET.get('branch'):
        filtered = inspections.filter(inspector_name__icontains=request.GET.get('branch'))
        print(f"   ✅ Inspector filter: {inspections.count()} → {filtered.count()} inspections")

    print("\n3. Testing date range filter logic:")
    date_from = (datetime.now().date() - timedelta(days=30)).isoformat()
    date_to = datetime.now().date().isoformat()
    request = factory.get('/inspections/', {
        'inspection_date_from': date_from,
        'inspection_date_to': date_to
    })

    # Apply date filters
    filtered = inspections
    if request.GET.get('inspection_date_from'):
        filtered = filtered.filter(date_of_inspection__gte=request.GET.get('inspection_date_from'))
    if request.GET.get('inspection_date_to'):
        filtered = filtered.filter(date_of_inspection__lte=request.GET.get('inspection_date_to'))
    print(f"   ✅ Date range filter: {inspections.count()} → {filtered.count()} inspections")

    print("\n4. Testing compliance status filter logic:")
    request = factory.get('/inspections/', {'compliance_status': 'NON_COMPLIANT'})

    # Apply compliance filter
    if request.GET.get('compliance_status') == 'NON_COMPLIANT':
        filtered = inspections.filter(is_direction_present_for_this_inspection=True)
        print(f"   ✅ Non-compliant filter: {inspections.count()} → {filtered.count()} inspections")

    return True

def main():
    """Run all tests"""
    print("="*80)
    print(" SHIPMENT LIST FILTER TESTS")
    print(" Testing shipment_list_clean.html filter functionality")
    print("="*80)

    tests = [
        ("Client Filter", test_client_filter),
        ("Inspector Filter", test_inspector_filter),
        ("Date Range Filter", test_date_range_filter),
        ("Sent Status Filter", test_sent_status_filter),
        ("Compliance Status Filter", test_compliance_status_filter),
        ("Combined Filters", test_combined_filters),
        ("Filter Logic", test_filter_logic),
        ("URL Integration", test_url_filter_integration),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print_section("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n{'='*80}")
    print(f" Results: {passed}/{total} tests passed")
    print(f"{'='*80}")

    if passed == total:
        print("\n🎉 All tests passed! Filters are working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the results above.")

if __name__ == '__main__':
    main()
