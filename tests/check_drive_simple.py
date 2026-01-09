import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.google_drive_service import GoogleDriveService

drive = GoogleDriveService()
parent_id = "1Q8ZXVC2NhzrPpDCdwfHGt8o726fLtqE_"

print("Fetching items from parent folder...")
items = drive.list_files_in_folder(parent_id, request=None, max_items=None)

print(f"\nFound {len(items)} items:")
for item in items:
    name = item.get('name', 'Unknown')
    mime = item.get('mimeType', '')
    is_folder = 'folder' in mime
    print(f"  {'[FOLDER]' if is_folder else '[FILE]'} {name}")
