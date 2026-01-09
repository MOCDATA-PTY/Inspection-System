import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.google_drive_service import GoogleDriveService

drive = GoogleDriveService()

# Get 2026/January folder
parent_id = "1Q8ZXVC2NhzrPpDCdwfHGt8o726fLtqE_"
items = drive.list_files_in_folder(parent_id, request=None, max_items=None)

for item in items:
    if item.get('name') == '2026':
        year_contents = drive.list_files_in_folder(item.get('id'), request=None, max_items=None)
        for month in year_contents:
            if 'January' in month.get('name', ''):
                print(f"Searching in {month.get('name')}...")
                all_files = drive.list_files_in_folder(month.get('id'), request=None, max_items=1000)
                print(f"Total files: {len(all_files)}")
                
                # Search for our account codes
                target_codes = ['RE-IND-EGG-NA-5042', 'RE-IND-EGG-NA-5053']
                
                print("\nSearching for target account codes...")
                found_any = False
                for f in all_files:
                    name = f.get('name', '')
                    for code in target_codes:
                        if code in name:
                            print(f"  FOUND: {name}")
                            found_any = True
                
                if not found_any:
                    print("  NOT FOUND - No files match those account codes")
                
                # Show all unique account code patterns
                print("\nAll EGG account codes in this folder:")
                egg_codes = set()
                for f in all_files:
                    name = f.get('name', '')
                    if name.startswith('Egg-') or name.startswith('EGG-'):
                        parts = name.split('-')
                        if len(parts) >= 6:
                            code = '-'.join(parts[1:6])
                            egg_codes.add(code)
                
                for code in sorted(egg_codes)[:20]:
                    print(f"  {code}")
                if len(egg_codes) > 20:
                    print(f"  ... and {len(egg_codes)-20} more")
