"""
Test the daily compliance sync to see if it's actually working
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.daily_compliance_sync import DailyComplianceSyncService
from django.http import HttpRequest

def test_daily_sync():
    print("=" * 80)
    print("TESTING DAILY COMPLIANCE SYNC")
    print("=" * 80)
    print()
    
    # Create service instance
    service = DailyComplianceSyncService()
    
    # Start the sync manually
    print("Starting daily sync...")
    request = HttpRequest()
    service.start_daily_sync(manual_start=True)
    
    # Wait a bit to see output
    import time
    time.sleep(5)
    
    print()
    print("Sync should be running in background")
    print("Check the console/terminal for sync output")

if __name__ == "__main__":
    test_daily_sync()

