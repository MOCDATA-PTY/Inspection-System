import os
import shutil
from pathlib import Path

# Base directory
MEDIA_ROOT = r'c:\Users\Ethan\Desktop\Inspection-System-master\Inspection-System-master\media\inspection'

def move_mobile_files():
    """Move files from mobile_ prefixed folders to their correct cleaned folders"""

    if not os.path.exists(MEDIA_ROOT):
        print(f"[ERROR] Media root not found: {MEDIA_ROOT}")
        return

    moved_count = 0
    error_count = 0

    # Walk through all directories
    for root, dirs, files in os.walk(MEDIA_ROOT):
        # Check if this is a mobile_ prefixed folder
        folder_name = os.path.basename(root)

        if folder_name.startswith('mobile_'):
            # Get the cleaned folder name
            cleaned_name = folder_name.replace('mobile_', '', 1)

            # Get parent directory
            parent_dir = os.path.dirname(root)

            # Destination folder
            dest_folder = os.path.join(parent_dir, cleaned_name)

            print(f"\n[FOUND] Mobile folder: {folder_name}")
            print(f"  Source: {root}")
            print(f"  Destination: {dest_folder}")

            # Create destination folder if it doesn't exist
            if not os.path.exists(dest_folder):
                print(f"  [CREATE] Creating destination folder: {cleaned_name}")
                os.makedirs(dest_folder, exist_ok=True)

            # Move all files from source to destination
            for file in files:
                source_file = os.path.join(root, file)
                dest_file = os.path.join(dest_folder, file)

                try:
                    # Check if file already exists in destination
                    if os.path.exists(dest_file):
                        print(f"  [SKIP] File already exists: {file}")
                    else:
                        shutil.move(source_file, dest_file)
                        print(f"  [MOVED] {file}")
                        moved_count += 1
                except Exception as e:
                    print(f"  [ERROR] Failed to move {file}: {str(e)}")
                    error_count += 1

            # Also check for subdirectories (like rfi/, invoice/, lab/)
            for subdir in os.listdir(root):
                subdir_path = os.path.join(root, subdir)
                if os.path.isdir(subdir_path):
                    dest_subdir = os.path.join(dest_folder, subdir)

                    # Create destination subdirectory if it doesn't exist
                    if not os.path.exists(dest_subdir):
                        print(f"  [CREATE] Creating subdirectory: {subdir}")
                        os.makedirs(dest_subdir, exist_ok=True)

                    # Move all files from source subdirectory to destination subdirectory
                    for subfile in os.listdir(subdir_path):
                        source_subfile = os.path.join(subdir_path, subfile)
                        if os.path.isfile(source_subfile):
                            dest_subfile = os.path.join(dest_subdir, subfile)

                            try:
                                if os.path.exists(dest_subfile):
                                    print(f"  [SKIP] File already exists: {subdir}/{subfile}")
                                else:
                                    shutil.move(source_subfile, dest_subfile)
                                    print(f"  [MOVED] {subdir}/{subfile}")
                                    moved_count += 1
                            except Exception as e:
                                print(f"  [ERROR] Failed to move {subdir}/{subfile}: {str(e)}")
                                error_count += 1

    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"  Files moved: {moved_count}")
    print(f"  Errors: {error_count}")
    print(f"{'='*60}")

if __name__ == '__main__':
    print("Moving files from mobile_ folders to cleaned folders...")
    print(f"Media root: {MEDIA_ROOT}\n")
    move_mobile_files()
    print("\nDone!")
