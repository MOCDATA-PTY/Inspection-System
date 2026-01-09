import os
from datetime import datetime

print("\n" + "="*80)
print("FINDING ALL LAB/COA FILES IN MEDIA FOLDER")
print("="*80 + "\n")

MEDIA_ROOT = '/root/Inspection-System/media/inspection'

if not os.path.exists(MEDIA_ROOT):
    print(f"ERROR: Media root not found: {MEDIA_ROOT}")
    exit(1)

print(f"Scanning: {MEDIA_ROOT}\n")

lab_folders = []
total_lab_files = 0

# Walk through all directories
for root, dirs, files in os.walk(MEDIA_ROOT):
    # Check if this is a Compliance folder
    if 'Compliance' in root:
        lab_files_in_folder = []

        for filename in files:
            filename_lower = filename.lower()
            # Check if it's a lab/COA file
            if ('lab' in filename_lower or
                filename_lower.startswith('fsl-') or
                filename_lower.startswith('lab-') or
                'coa' in filename_lower):

                file_path = os.path.join(root, filename)
                file_size = os.path.getsize(file_path)
                file_date = datetime.fromtimestamp(os.path.getmtime(file_path))

                lab_files_in_folder.append({
                    'name': filename,
                    'path': file_path,
                    'size': file_size,
                    'modified': file_date
                })
                total_lab_files += 1

        if lab_files_in_folder:
            lab_folders.append({
                'folder': root,
                'files': lab_files_in_folder
            })

# Also check for lab files in non-Compliance folders
for root, dirs, files in os.walk(MEDIA_ROOT):
    if 'Compliance' not in root:  # Skip Compliance folders (already checked)
        lab_files_in_folder = []

        for filename in files:
            filename_lower = filename.lower()
            if ('lab' in filename_lower or
                filename_lower.startswith('fsl-') or
                filename_lower.startswith('lab-') or
                'coa' in filename_lower):

                file_path = os.path.join(root, filename)
                file_size = os.path.getsize(file_path)
                file_date = datetime.fromtimestamp(os.path.getmtime(file_path))

                lab_files_in_folder.append({
                    'name': filename,
                    'path': file_path,
                    'size': file_size,
                    'modified': file_date
                })
                total_lab_files += 1

        if lab_files_in_folder:
            lab_folders.append({
                'folder': root,
                'files': lab_files_in_folder
            })

print("="*80)
print(f"RESULTS: Found {total_lab_files} lab/COA files in {len(lab_folders)} folders")
print("="*80 + "\n")

# Sort by folder path
lab_folders.sort(key=lambda x: x['folder'])

for folder_info in lab_folders:
    folder = folder_info['folder']
    files = folder_info['files']

    # Extract client name from path
    parts = folder.replace(MEDIA_ROOT, '').strip('/').split('/')
    if len(parts) >= 3:
        year = parts[0]
        month = parts[1]
        client = parts[2]
        print(f"[{year}/{month}] {client}")
    else:
        print(f"Folder: {folder}")

    print(f"  Location: {folder}")
    print(f"  Files ({len(files)}):")

    for file_info in files:
        size_kb = file_info['size'] / 1024
        print(f"    - {file_info['name']}")
        print(f"      Size: {size_kb:.1f} KB, Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M')}")
    print()

print("="*80)
print(f"SUMMARY:")
print(f"  Total folders with lab files: {len(lab_folders)}")
print(f"  Total lab files found: {total_lab_files}")
print("="*80)
