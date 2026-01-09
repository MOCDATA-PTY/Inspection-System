"""
Check actual folder structure for Avonlea Farm CC
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings


def check_folders():
    """Check actual folder structure"""

    media_root = settings.MEDIA_ROOT
    client_path = os.path.join(media_root, 'inspection', '2025', 'November', 'avonlea_farm_cc')

    print("\n" + "="*100)
    print(f"Checking folder: {client_path}")
    print("="*100 + "\n")

    if os.path.exists(client_path):
        print("Folders in avonlea_farm_cc:")
        for item in os.listdir(client_path):
            item_path = os.path.join(client_path, item)
            if os.path.isdir(item_path):
                print(f"\n  Folder: {item}")
                # List files in this folder
                try:
                    files = os.listdir(item_path)
                    if files:
                        print(f"  Files ({len(files)}):")
                        for f in files:
                            print(f"    - {f}")
                    else:
                        print("    (empty)")
                except Exception as e:
                    print(f"    Error: {e}")
            else:
                print(f"\n  File (in root): {item}")
    else:
        print("Path does not exist!")
        print(f"\nLet me check what exists at inspection/2025/November/:")
        nov_path = os.path.join(media_root, 'inspection', '2025', 'November')
        if os.path.exists(nov_path):
            print("\nFolders in November 2025:")
            for item in sorted(os.listdir(nov_path)):
                print(f"  - {item}")

    print("\n" + "="*100 + "\n")


if __name__ == "__main__":
    try:
        check_folders()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
