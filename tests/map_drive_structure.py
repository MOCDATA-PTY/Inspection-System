import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.google_drive_service import GoogleDriveService

drive = GoogleDriveService()
parent_id = "1Q8ZXVC2NhzrPpDCdwfHGt8o726fLtqE_"

print("MAPPING GOOGLE DRIVE STRUCTURE")
print("=" * 60)

# Get top level items
top_items = drive.list_files_in_folder(parent_id, request=None, max_items=None)
print(f"\nPARENT FOLDER: {parent_id}")
print(f"Contains {len(top_items)} items:\n")

for item in top_items:
    name = item.get('name', '')
    item_id = item.get('id', '')
    is_folder = 'folder' in item.get('mimeType', '')
    
    if is_folder:
        print(f"[FOLDER] {name}")
        
        # Get subfolders (months)
        sub_items = drive.list_files_in_folder(item_id, request=None, max_items=None)
        
        for sub in sub_items:
            sub_name = sub.get('name', '')
            sub_id = sub.get('id', '')
            sub_is_folder = 'folder' in sub.get('mimeType', '')
            
            if sub_is_folder:
                # Get files in month folder
                files = drive.list_files_in_folder(sub_id, request=None, max_items=None)
                print(f"    [MONTH] {sub_name} ({len(files)} files)")
                
                # Show first 3 files as sample
                for f in files[:3]:
                    print(f"        - {f.get('name', '')}")
                if len(files) > 3:
                    print(f"        ... and {len(files)-3} more files")
            else:
                print(f"    [FILE] {sub_name}")
    else:
        print(f"[FILE] {name}")

print("\n" + "=" * 60)
