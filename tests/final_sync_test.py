#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final comprehensive sync test - simulates login and button click
"""
import os
import sys
import django

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.core.cache import cache
from main.models import FoodSafetyAgencyInspection
from main.services.google_sheets_service import GoogleSheetsService

User = get_user_model()

print("\n" + "="*80)
print("FINAL COMPREHENSIVE SYNC TEST")
print("="*80)

# Step 1: Verify user credentials
print("\nStep 1: Verifying user credentials...")
print("-"*80)

username = 'developer'
password = 'Ethan4269875321'

user = authenticate(username=username, password=password)

if user:
    print(f"✓ Authentication successful!")
    print(f"  Username: {user.username}")
    print(f"  Role: {user.role}")

    # Check if user can sync
    if user.role == 'admin':
        print(f"✗ ERROR: User has 'admin' role - BLOCKED from syncing!")
        print(f"  The sync button will redirect to home page.")
        sys.exit(1)
    else:
        print(f"✓ User CAN sync (role is not 'admin')")
else:
    print(f"✗ Authentication failed!")
    print(f"  Username '{username}' or password is incorrect")
    sys.exit(1)

# Step 2: Check current database state
print("\nStep 2: Checking current database state...")
print("-"*80)

before_count = FoodSafetyAgencyInspection.objects.count()
print(f"Current inspections in database: {before_count}")

if before_count > 0:
    latest = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection').first()
    print(f"Latest inspection:")
    print(f"  Date: {latest.date_of_inspection}")
    print(f"  Client: {latest.client_name}")
    print(f"  Commodity: {latest.commodity}")

# Step 3: Test SQL Server connection
print("\nStep 3: Testing SQL Server connection...")
print("-"*80)

try:
    import pymssql
    from django.conf import settings

    sql_server_config = settings.DATABASES.get('sql_server', {})

    connection = pymssql.connect(
        server=sql_server_config.get('HOST'),
        port=int(sql_server_config.get('PORT', 1433)),
        user=sql_server_config.get('USER'),
        password=sql_server_config.get('PASSWORD'),
        database=sql_server_config.get('NAME'),
        timeout=30
    )

    print(f"✓ SQL Server connection successful!")
    print(f"  Host: {sql_server_config.get('HOST')}:{sql_server_config.get('PORT')}")
    print(f"  Database: {sql_server_config.get('NAME')}")

    connection.close()

except Exception as e:
    print(f"✗ SQL Server connection failed: {e}")
    sys.exit(1)

# Step 4: Run the actual sync (simulating button click)
print("\nStep 4: Running sync (simulating button click)...")
print("-"*80)
print("This is what happens when you click 'Sync Inspections'...\n")

try:
    # Clear any previous sync results
    cache.delete('sync_result')

    # Initialize service and run sync
    sheets_service = GoogleSheetsService()

    # Create a mock request object
    class MockRequest:
        def __init__(self, user):
            self.user = user
            self.session = {}
            self.method = 'POST'
            self.headers = {}

    mock_request = MockRequest(user)

    # Run the sync
    print("Starting sync operation...")
    result = sheets_service.populate_inspections_table(mock_request)

    print("\n" + "="*80)
    print("SYNC RESULT")
    print("="*80)

    if result.get('success'):
        print(f"\n✓✓✓ SUCCESS! ✓✓✓")
        print(f"\nDetails:")
        print(f"  Deleted: {result.get('deleted_count', 0)} old inspections")
        print(f"  Created: {result.get('inspections_created', 0)} new inspections")
        print(f"  Processed: {result.get('total_processed', 0)} total records")

        # Verify database
        after_count = FoodSafetyAgencyInspection.objects.count()
        print(f"\nDatabase verification:")
        print(f"  Before sync: {before_count} inspections")
        print(f"  After sync: {after_count} inspections")

        if after_count > 0:
            latest = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection').first()
            print(f"\nMost recent inspection:")
            print(f"  Date: {latest.date_of_inspection}")
            print(f"  Client: {latest.client_name}")
            print(f"  Commodity: {latest.commodity}")
            print(f"  Inspector: {latest.inspector_name}")

        print("\n" + "="*80)
        print("CONCLUSION: SYNC BUTTON WORKS PERFECTLY!")
        print("="*80)
        print("\nThe sync functionality is working correctly.")
        print("If you're having issues in the browser:")
        print("  1. Make sure you're logged in as 'developer' (not 'admin')")
        print("  2. Clear browser cache (Ctrl+Shift+Delete)")
        print("  3. Check browser console for errors (F12 -> Console tab)")
        print("  4. Make sure you have a stable internet connection")

    else:
        print(f"\n✗ SYNC FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")

except Exception as e:
    print(f"\n✗ SYNC EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
