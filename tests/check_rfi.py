"""
Check for recently uploaded RFI files
"""

import os
import django
import sys
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings


def check_recent_rfi_files():
    """Check for RFI files uploaded in the last hour"""

    print("\n" + "="*100)
    print("CHECKING FOR RECENTLY UPLOADED RFI FILES")
    print("="*100 + "\n")

    media_root = settings.MEDIA_ROOT
    print(f"Media Root: {media_root}\n")

    # Find all RFI files modified in the last hour
    recent_files = []
    one_hour_ago = datetime.now() - timedelta(hours=1)

    for root, dirs, files in os.walk(media_root):
        for filename in files:
            if 'rfi' in filename.lower():
                file_path = os.path.join(root, filename)
                modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                if modified_time > one_hour_ago:
                    relative_path = os.path.relpath(file_path, media_root)
                    recent_files.append({
                        'filename': filename,
                        'path': relative_path,
                        'full_path': file_path,
                        'modified': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'size': os.path.getsize(file_path)
                    })

    if recent_files:
        print(f"Found {len(recent_files)} RFI file(s) uploaded in the last hour:\n")
        for idx, f in enumerate(recent_files, 1):
            print(f"File #{idx}:")
            print(f"  Name: {f['filename']}")
            print(f"  Path: {f['path']}")
            print(f"  Modified: {f['modified']}")
            print(f"  Size: {f['size']:,} bytes")
            print()
    else:
        print("No RFI files found uploaded in the last hour.")
        print("\nShowing ALL RFI files in media folder:\n")

        all_rfi_files = []
        for root, dirs, files in os.walk(media_root):
            for filename in files:
                if 'rfi' in filename.lower():
                    file_path = os.path.join(root, filename)
                    modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    relative_path = os.path.relpath(file_path, media_root)
                    all_rfi_files.append({
                        'filename': filename,
                        'path': relative_path,
                        'modified': modified_time.strftime('%Y-%m-%d %H:%M:%S')
                    })

        if all_rfi_files:
            # Sort by modified time, newest first
            all_rfi_files.sort(key=lambda x: x['modified'], reverse=True)
            print(f"Total RFI files: {len(all_rfi_files)}\n")
            print("Most recent 10 RFI files:")
            for idx, f in enumerate(all_rfi_files[:10], 1):
                print(f"{idx}. {f['filename']}")
                print(f"   Path: {f['path']}")
                print(f"   Modified: {f['modified']}")
                print()
        else:
            print("No RFI files found in media folder at all.")

    print("="*100 + "\n")


if __name__ == "__main__":
    try:
        check_recent_rfi_files()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
