import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.google_drive_service import GoogleDriveService

drive = GoogleDriveService()
parent_id = "1Q8ZXVC2NhzrPpDCdwfHGt8o726fLtqE_"

# First get all items
items = drive.list_files_in_folder(parent_id, request=None, max_items=None)

# Find 2026 folder
folder_2026 = None
for item in items:
    if item.get('name') == '2026' and 'folder' in item.get('mimeType', ''):
        folder_2026 = item
        break

if folder_2026:
    print(f"Found 2026 folder: {folder_2026.get('id')}")
    
    # Get contents of 2026
    contents = drive.list_files_in_folder(folder_2026.get('id'), request=None, max_items=None)
    print(f"\n2026 folder contains {len(contents)} items:")
    
    for item in contents:
        name = item.get('name', 'Unknown')
        mime = item.get('mimeType', '')
        is_folder = 'folder' in mime
        print(f"  {'[FOLDER]' if is_folder else '[FILE]'} {name}")
        
        # If it's January folder, show its contents
        if is_folder and 'January' in name:
            jan_contents = drive.list_files_in_folder(item.get('id'), request=None, max_items=20)
            print(f"    -> Contains {len(jan_contents)} files")
            for f in jan_contents[:10]:
                print(f"       - {f.get('name', 'Unknown')}")
else:
    print("2026 folder not found!")
