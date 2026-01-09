#!/usr/bin/env python
"""
Quick test to verify Google Sheets status check
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def test_google_sheets_status():
    """Test Google Sheets status check"""
    print("🔍 TESTING GOOGLE SHEETS STATUS CHECK")
    print("="*50)
    
    try:
        from main.views.core_views import check_google_sheets_status
        
        # Test the status check
        is_connected = check_google_sheets_status()
        
        print(f"📊 Google Sheets Status: {'✅ Connected' if is_connected else '❌ Disconnected'}")
        
        if is_connected:
            print("🎉 SUCCESS! Google Sheets should now show as 'Connected' on the home page.")
        else:
            print("⚠️  Google Sheets status check returned False")
            
        return is_connected
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_google_sheets_status()
    sys.exit(0 if success else 1)
