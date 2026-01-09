#!/usr/bin/env python3
"""
Force clear all Python bytecode cache to ensure new code runs.
This deletes all .pyc files and __pycache__ directories.
"""
import os
import shutil

def clear_pycache(root_dir):
    """Recursively delete all __pycache__ directories and .pyc files."""
    deleted_dirs = 0
    deleted_files = 0

    for root, dirs, files in os.walk(root_dir):
        # Delete __pycache__ directories
        if '__pycache__' in dirs:
            cache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(cache_path)
                deleted_dirs += 1
                print(f"Deleted: {cache_path}")
            except Exception as e:
                print(f"Error deleting {cache_path}: {e}")

        # Delete .pyc files
        for file in files:
            if file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    deleted_files += 1
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

    return deleted_dirs, deleted_files

if __name__ == '__main__':
    print("=" * 80)
    print("FORCE CLEARING PYTHON BYTECODE CACHE")
    print("=" * 80)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\nScanning directory: {current_dir}")
    print()

    dirs, files = clear_pycache(current_dir)

    print()
    print("=" * 80)
    print(f"SUMMARY: Deleted {dirs} __pycache__ directories and {files} .pyc files")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Run this on production server: python3 force_clear_cache.py")
    print("2. Restart Gunicorn: sudo systemctl restart gunicorn")
    print("3. Check Gunicorn status: sudo systemctl status gunicorn")
    print("4. Test the export again")
    print()