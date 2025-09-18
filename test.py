#!/usr/bin/env python
"""
Test script to verify system status functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def test_system_status():
    """Test all system status checks"""
    print("🔍 TESTING SYSTEM STATUS FUNCTIONALITY")
    print("="*60)
    
    # Import the status check functions from the home view
    from main.views.core_views import home
    from django.test import RequestFactory
    from django.contrib.auth import get_user_model
    
    try:
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/')
        
        # Get a test user
        User = get_user_model()
        test_user = User.objects.filter(role__in=['developer', 'inspector']).first()
        if not test_user:
            print("❌ No test user found")
            return False
        
        request.user = test_user
        
        # Test individual status functions
        print("\n📊 Testing individual status checks...")
        
        # Test PostgreSQL status
        print("1. Testing PostgreSQL status...")
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                postgresql_status = True if result else False
            print(f"   ✅ PostgreSQL: {'Online' if postgresql_status else 'Offline'}")
        except Exception as e:
            print(f"   ❌ PostgreSQL: Offline ({e})")
            postgresql_status = False
        
        # Test SQL Server status
        print("2. Testing SQL Server status...")
        try:
            import pyodbc
            from main.views.data_views import SQLSERVER_CONNECTION_STRING
            
            conn = pyodbc.connect(SQLSERVER_CONNECTION_STRING, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            sql_server_status = True if result else False
            print(f"   ✅ SQL Server: {'Online' if sql_server_status else 'Offline'}")
        except Exception as e:
            print(f"   ❌ SQL Server: Offline ({e})")
            sql_server_status = False
        
        # Test Google Sheets status
        print("3. Testing Google Sheets status...")
        try:
            from main.services.google_sheets_service import GoogleSheetsService
            import pickle
            
            service = GoogleSheetsService()
            google_sheets_status = False
            
            if os.path.exists(service.token_path):
                with open(service.token_path, 'rb') as token:
                    creds = pickle.load(token)
                    if creds and creds.valid:
                        try:
                            sheets_service = service.authenticate_google_sheets()
                            if sheets_service:
                                google_sheets_status = True
                        except:
                            pass
            
            print(f"   ✅ Google Sheets: {'Connected' if google_sheets_status else 'Disconnected'}")
        except Exception as e:
            print(f"   ❌ Google Sheets: Disconnected ({e})")
            google_sheets_status = False
        
        # Test last sync status
        print("4. Testing last sync status...")
        try:
            from main.models import FoodSafetyAgencyInspection
            from django.utils import timezone
            
            latest_inspection = FoodSafetyAgencyInspection.objects.order_by('-created_at').first()
            if latest_inspection:
                now = timezone.now()
                created_at = latest_inspection.created_at
                
                # Handle timezone-aware datetime comparison
                if timezone.is_aware(created_at) and not timezone.is_aware(now):
                    now = timezone.make_aware(now)
                elif not timezone.is_aware(created_at) and timezone.is_aware(now):
                    created_at = timezone.make_aware(created_at)
                
                time_diff = now - created_at
                if time_diff.total_seconds() < 3600:  # Less than 1 hour
                    last_sync = "Just now"
                elif time_diff.total_seconds() < 86400:  # Less than 1 day
                    hours = int(time_diff.total_seconds() / 3600)
                    last_sync = f"{hours} hour{'s' if hours > 1 else ''} ago"
                else:
                    days = int(time_diff.total_seconds() / 86400)
                    last_sync = f"{days} day{'s' if days > 1 else ''} ago"
            else:
                last_sync = "No data"
            
            print(f"   ✅ Last Sync: {last_sync}")
        except Exception as e:
            print(f"   ❌ Last Sync: Unknown ({e})")
            last_sync = "Unknown"
        
        # Test cache functionality
        print("\n💾 Testing cache functionality...")
        try:
            from django.core.cache import cache
            
            # Test cache set/get
            cache.set('test_status', True, 30)
            cached_value = cache.get('test_status')
            cache_working = cached_value == True
            
            print(f"   ✅ Cache: {'Working' if cache_working else 'Not working'}")
        except Exception as e:
            print(f"   ❌ Cache: Not working ({e})")
            cache_working = False
        
        # Summary
        print("\n" + "="*60)
        print("📋 SYSTEM STATUS SUMMARY")
        print("="*60)
        print(f"🗄️  PostgreSQL:    {'✅ Online' if postgresql_status else '❌ Offline'}")
        print(f"💾 SQL Server:     {'✅ Online' if sql_server_status else '❌ Offline'}")
        print(f"📊 Google Sheets:  {'✅ Connected' if google_sheets_status else '❌ Disconnected'}")
        print(f"⏰ Last Sync:      {last_sync}")
        print(f"🔄 Cache System:   {'✅ Working' if cache_working else '❌ Not working'}")
        
        # Overall assessment
        all_systems_good = postgresql_status and sql_server_status and google_sheets_status and cache_working
        
        print("\n" + "="*60)
        if all_systems_good:
            print("🎉 ALL SYSTEMS OPERATIONAL!")
            print("   The system status display should show all services as connected/online.")
        else:
            print("⚠️  SOME SYSTEMS HAVE ISSUES")
            print("   Check the individual status messages above for details.")
        print("="*60)
        
        return all_systems_good
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_home_page_access():
    """Test if the home page loads without errors"""
    print("\n🌐 TESTING HOME PAGE ACCESS")
    print("="*40)
    
    try:
        import requests
        response = requests.get('http://127.0.0.1:8000/', timeout=10)
        
        if response.status_code == 200:
            print("✅ Home page loads successfully")
            
            # Check if system status section exists
            if 'System Status' in response.text:
                print("✅ System Status section found")
                
                # Check for status indicators
                if 'PostgreSQL' in response.text:
                    print("✅ PostgreSQL status displayed")
                if 'SQL Server' in response.text:
                    print("✅ SQL Server status displayed")
                if 'Google Sheets' in response.text:
                    print("✅ Google Sheets status displayed")
                
                return True
            else:
                print("❌ System Status section not found")
                return False
        else:
            print(f"❌ Home page returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running on http://127.0.0.1:8000/")
        return False
    except Exception as e:
        print(f"❌ Home page test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 STARTING SYSTEM STATUS TESTS")
    print("="*80)
    
    # Test 1: System status functionality
    status_test_passed = test_system_status()
    
    # Test 2: Home page access
    home_page_test_passed = test_home_page_access()
    
    # Final summary
    print("\n" + "="*80)
    print("🏁 FINAL TEST RESULTS")
    print("="*80)
    print(f"🔧 System Status Test: {'✅ PASSED' if status_test_passed else '❌ FAILED'}")
    print(f"🌐 Home Page Test: {'✅ PASSED' if home_page_test_passed else '❌ FAILED'}")
    
    if status_test_passed and home_page_test_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("   The system status functionality is working correctly.")
        print("   Refresh your home page to see the updated status indicators.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return status_test_passed and home_page_test_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)