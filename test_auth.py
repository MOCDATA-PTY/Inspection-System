"""
Test Google Sheets authentication and create token.pickle
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.google_sheets_service import GoogleSheetsService
from django.test import RequestFactory

print("\n" + "="*80)
print("Testing Google Sheets Authentication")
print("="*80 + "\n")

# Create a fake request object
factory = RequestFactory()
request = factory.get('/fake-path')
request.session = {}

try:
    print("[INFO] Creating GoogleSheetsService instance...")
    sheets_service = GoogleSheetsService()

    print("[INFO] Calling authenticate()...")
    sheets_service.authenticate(request)

    print("[SUCCESS] Authentication completed!")

    # Check if token.pickle was created
    if os.path.exists('token.pickle'):
        file_size = os.path.getsize('token.pickle')
        print(f"[SUCCESS] token.pickle created! Size: {file_size} bytes")
    else:
        print("[WARNING] token.pickle not found after authentication")

    print("\n" + "="*80)
    print("DONE!")
    print("="*80 + "\n")

except Exception as e:
    print(f"[ERROR] Authentication failed: {e}")
    import traceback
    traceback.print_exc()
