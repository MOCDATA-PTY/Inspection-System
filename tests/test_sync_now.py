#!/usr/bin/env python
"""
Test sync functionality to diagnose why sync isn't working
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.scheduled_sync_service import ScheduledSyncService

print("="*80)
print("TESTING SQL SERVER SYNC")
print("="*80)

service = ScheduledSyncService()

print("\n1. Checking SQL Server connection settings...")
from django.conf import settings
sql_config = settings.DATABASES.get('sql_server', {})
print(f"   Host: {sql_config.get('HOST')}")
print(f"   Database: {sql_config.get('NAME')}")
print(f"   User: {sql_config.get('USER')}")
print(f"   Has password: {'Yes' if sql_config.get('PASSWORD') else 'No'}")

print("\n2. Running SQL Server sync...")
try:
    result = service.sync_sql_server()
    print(f"\n✅ SYNC COMPLETED!")
    print(f"Result: {result}")
except Exception as e:
    print(f"\n❌ SYNC FAILED!")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Checking database after sync...")
from main.models import FoodSafetyAgencyInspection
count = FoodSafetyAgencyInspection.objects.count()
print(f"   Total inspections: {count}")
km_count = FoodSafetyAgencyInspection.objects.filter(km_traveled__isnull=False).exclude(km_traveled=0).count()
print(f"   With km/hours: {km_count}")

print("\n" + "="*80)
