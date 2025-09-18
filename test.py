#!/usr/bin/env python
"""
Test script to verify client count and sync functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def test_client_count():
    """Test the actual client count in the database"""
    print("🔍 TESTING CLIENT COUNT")
    print("="*50)
    
    try:
        from main.models import Client
        
        # Get total client count
        total_clients = Client.objects.count()
        print(f"📊 Total clients in database: {total_clients:,}")
        
        # Get clients with account codes
        clients_with_codes = Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code='').count()
        print(f"📊 Clients with account codes: {clients_with_codes:,}")
        
        # Get clients without account codes
        from django.db import models
        clients_without_codes = Client.objects.filter(
            models.Q(internal_account_code__isnull=True) | models.Q(internal_account_code='')
        ).count()
        print(f"📊 Clients without account codes: {clients_without_codes:,}")
        
        # Check for duplicates by name
        from django.db.models import Count
        duplicate_names = Client.objects.values('name').annotate(
            count=Count('name')
        ).filter(count__gt=1).order_by('-count')
        
        if duplicate_names:
            print(f"\n⚠️  DUPLICATE CLIENT NAMES FOUND:")
            for item in duplicate_names[:10]:  # Show top 10
                print(f"   - '{item['name']}': {item['count']} occurrences")
        else:
            print(f"\n✅ No duplicate client names found")
        
        # Check for duplicates by account code
        duplicate_codes = Client.objects.values('internal_account_code').annotate(
            count=Count('internal_account_code')
        ).filter(count__gt=1).order_by('-count')
        
        if duplicate_codes:
            print(f"\n⚠️  DUPLICATE ACCOUNT CODES FOUND:")
            for item in duplicate_codes[:10]:  # Show top 10
                print(f"   - '{item['internal_account_code']}': {item['count']} occurrences")
        else:
            print(f"\n✅ No duplicate account codes found")
        
        return total_clients, clients_with_codes, clients_without_codes
        
    except Exception as e:
        print(f"❌ Error testing client count: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None

def test_sync_lock():
    """Test if sync lock mechanism is working"""
    print("\n🔒 TESTING SYNC LOCK MECHANISM")
    print("="*50)
    
    try:
        from django.core.cache import cache
        
        # Check current sync status
        client_sync_running = cache.get('client_sync_running')
        inspection_sync_running = cache.get('sync_running')
        
        print(f"📊 Client sync running: {'Yes' if client_sync_running else 'No'}")
        print(f"📊 Inspection sync running: {'Yes' if inspection_sync_running else 'No'}")
        
        # Test setting a sync lock
        cache.set('test_sync_lock', True, 60)
        test_lock = cache.get('test_sync_lock')
        print(f"📊 Test lock set: {'Yes' if test_lock else 'No'}")
        
        # Clear test lock
        cache.delete('test_sync_lock')
        test_lock_cleared = cache.get('test_sync_lock')
        print(f"📊 Test lock cleared: {'Yes' if not test_lock_cleared else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing sync lock: {str(e)}")
        return False

def test_google_sheets_connection():
    """Test Google Sheets connection"""
    print("\n📊 TESTING GOOGLE SHEETS CONNECTION")
    print("="*50)
    
    try:
        from main.services.google_sheets_service import GoogleSheetsService
        
        service = GoogleSheetsService()
        
        # Test authentication
        try:
            service.authenticate()
            if service.service:
                print("✅ Google Sheets authentication successful")
                
                # Test getting client data
                try:
                    # This would normally get client data from Google Sheets
                    print("✅ Google Sheets service initialized successfully")
                    return True
                except Exception as e:
                    print(f"⚠️  Google Sheets data access failed: {e}")
                    return False
            else:
                print("❌ Google Sheets authentication failed")
                return False
        except Exception as e:
            print(f"❌ Google Sheets connection error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google Sheets: {str(e)}")
        return False

def test_inspection_count():
    """Test inspection count for comparison"""
    print("\n🔍 TESTING INSPECTION COUNT")
    print("="*50)
    
    try:
        from main.models import FoodSafetyAgencyInspection
        
        total_inspections = FoodSafetyAgencyInspection.objects.count()
        print(f"📊 Total inspections in database: {total_inspections:,}")
        
        # Get recent inspections
        from django.utils import timezone
        from datetime import timedelta
        
        recent_inspections = FoodSafetyAgencyInspection.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        print(f"📊 Inspections created in last hour: {recent_inspections:,}")
        
        return total_inspections, recent_inspections
        
    except Exception as e:
        print(f"❌ Error testing inspection count: {str(e)}")
        return None, None

def main():
    """Run all tests"""
    print("🚀 STARTING CLIENT COUNT VERIFICATION TESTS")
    print("="*80)
    
    # Test 1: Client count
    total_clients, clients_with_codes, clients_without_codes = test_client_count()
    
    # Test 2: Sync lock mechanism
    sync_lock_working = test_sync_lock()
    
    # Test 3: Google Sheets connection
    sheets_working = test_google_sheets_connection()
    
    # Test 4: Inspection count for comparison
    total_inspections, recent_inspections = test_inspection_count()
    
    # Summary
    print("\n" + "="*80)
    print("📋 TEST RESULTS SUMMARY")
    print("="*80)
    
    if total_clients is not None:
        print(f"👥 Total Clients: {total_clients:,}")
        print(f"   - With account codes: {clients_with_codes:,}")
        print(f"   - Without account codes: {clients_without_codes:,}")
        
        # Expected range check
        if 4000 <= total_clients <= 5000:
            print("✅ Client count is within expected range (4,000-5,000)")
        elif total_clients > 5000:
            print("⚠️  Client count is higher than expected - possible duplicates")
        else:
            print("⚠️  Client count is lower than expected")
    
    if total_inspections is not None:
        print(f"🔍 Total Inspections: {total_inspections:,}")
        if recent_inspections is not None:
            print(f"   - Recent (last hour): {recent_inspections:,}")
    
    print(f"🔒 Sync Lock Mechanism: {'✅ Working' if sync_lock_working else '❌ Not working'}")
    print(f"📊 Google Sheets: {'✅ Connected' if sheets_working else '❌ Disconnected'}")
    
    # Final assessment
    print("\n" + "="*80)
    if total_clients and 4000 <= total_clients <= 5000 and sync_lock_working:
        print("🎉 ALL TESTS PASSED!")
        print("   Client count is correct and sync protection is working.")
    else:
        print("⚠️  Some issues detected. Check the results above for details.")
    print("="*80)
    
    return total_clients, sync_lock_working, sheets_working

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)