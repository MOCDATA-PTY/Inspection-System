#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test SQL Server sync with new comprehensive logging
Run this to see the detailed terminal output showing account code matching
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

from main.services.scheduled_sync_service import ScheduledSyncService

print("\n" + "="*80)
print("TESTING SQL SERVER SYNC WITH NEW LOGGING")
print("="*80)
print("\nThis test will:")
print("  1. Connect to SQL Server")
print("  2. Fetch inspections with account codes")
print("  3. Match account codes with Google Sheets Client table")
print("  4. Show detailed logs of what's happening")
print("  5. Display comprehensive statistics at the end")
print("\n" + "="*80)

input("\nPress Enter to start the sync (or Ctrl+C to cancel)...")

try:
    # Create sync service
    service = ScheduledSyncService()

    # Run SQL Server sync with new logging
    success = service.sync_sql_server()

    if success:
        print("\n" + "="*80)
        print("✅ SYNC TEST COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nCheck the logs above to see:")
        print("  ✓ How many inspections have account codes")
        print("  ✓ How many matched with Google Sheets")
        print("  ✓ Which client names are being used (Google Sheets vs SQL Server)")
        print("  ✓ Detailed processing for first 5 and every 10th inspection")
        print("\n" + "="*80)
    else:
        print("\n❌ SYNC FAILED - Check error messages above")

except KeyboardInterrupt:
    print("\n\n❌ Test cancelled by user")
    sys.exit(1)
except Exception as e:
    print(f"\n\n❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
