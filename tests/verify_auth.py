"""
Verify Google Sheets authentication is working
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.google_sheets_service import GoogleSheetsService

print("\n" + "="*80)
print("Verifying Google Sheets Authentication")
print("="*80 + "\n")

try:
    sheets_service = GoogleSheetsService()

    # Check connection status
    is_connected, message = sheets_service.check_connection_status()

    if is_connected:
        print("[SUCCESS] Google Sheets authentication is working!")
        print(f"[INFO] Status: {message}")
    else:
        print(f"[WARNING] Connection check returned: {message}")

    print("\n" + "="*80)
    print("Verification complete!")
    print("="*80 + "\n")

except Exception as e:
    print(f"[ERROR] Verification failed: {e}")
    import traceback
    traceback.print_exc()
