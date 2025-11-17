"""
Delete all files from inspection directories containing 'new' in the name
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings


def delete_new_inspection_files():
    """Delete all files from directories with 'new' in the name"""
    media_root = settings.MEDIA_ROOT

    print("\n" + "="*100)
    print("DELETING FILES FROM 'NEW' INSPECTION DIRECTORIES")
    print("="*100 + "\n")

    if not os.path.exists(media_root):
        print("ERROR: Media folder does not exist!")
        return

    # Find all files in directories containing 'new'
    files_to_delete = []

    for root, dirs, files in os.walk(media_root):
        # Check if 'new' is in the directory path (case insensitive)
        if 'new' in root.lower():
            for filename in files:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, media_root)
                files_to_delete.append({
                    'path': file_path,
                    'relative': relative_path,
                    'name': filename
                })

    if not files_to_delete:
        print("No files found in 'new' inspection directories.")
        return

    # Show what will be deleted
    print(f"Found {len(files_to_delete)} files in 'new' inspection directories:\n")
    for f in files_to_delete:
        print(f"  - {f['relative']}")

    # Confirm deletion
    print(f"\n{'-'*100}")
    confirm = input(f"\nDelete all {len(files_to_delete)} files? (yes/no): ").strip().lower()

    if confirm == 'yes':
        deleted = 0
        errors = 0

        for f in files_to_delete:
            try:
                os.remove(f['path'])
                deleted += 1
                print(f"[OK] Deleted: {f['name']}")
            except Exception as e:
                errors += 1
                print(f"[ERROR] Failed to delete {f['name']}: {e}")

        print(f"\n{'-'*100}")
        print(f"SUMMARY:")
        print(f"  Successfully deleted: {deleted} files")
        print(f"  Errors: {errors} files")
        print(f"{'-'*100}\n")
    else:
        print("\nDeletion cancelled.\n")


if __name__ == "__main__":
    try:
        delete_new_inspection_files()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
