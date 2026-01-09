#!/usr/bin/env python
"""
Remove all files for clients starting with "New" from media folder
Creates a backup list before deletion
"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def remove_new_client_files(media_path='media', dry_run=False):
    """
    Remove all files for clients starting with 'New'

    Args:
        media_path: Path to media folder
        dry_run: If True, only show what would be deleted without actually deleting
    """

    if not os.path.exists(media_path):
        print(f"ERROR: Media folder not found at: {media_path}")
        return

    print("="*100)
    print("REMOVE FILES FOR CLIENTS STARTING WITH 'NEW'")
    print("="*100)
    print(f"Scanning: {os.path.abspath(media_path)}")
    if dry_run:
        print("DRY RUN MODE - No files will be deleted")
    print("="*100)

    # List to store what will be deleted
    files_to_delete = []
    folders_to_delete = set()
    total_size = 0

    # Walk through media folder
    for root, dirs, files in os.walk(media_path):
        # Check if any part of the path contains a folder starting with "new"
        path_parts = root.split(os.sep)

        # Look for folders containing "new" (case-insensitive)
        is_new_client = any(part.lower().startswith('new') or 'new_' in part.lower()
                           for part in path_parts)

        if is_new_client:
            # Add this folder to deletion list
            folders_to_delete.add(root)

            # Add all files in this folder
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    files_to_delete.append({
                        'path': file_path,
                        'rel_path': os.path.relpath(file_path, media_path),
                        'size': file_size
                    })
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")

    # Show what will be deleted
    print(f"\nFound {len(files_to_delete)} files in {len(folders_to_delete)} folders to delete")
    print(f"Total size: {format_size(total_size)}\n")

    if len(files_to_delete) == 0:
        print("No files found for clients starting with 'New'")
        return

    # Group by client folder for display
    client_folders = {}
    for file_info in files_to_delete:
        # Extract client folder name
        parts = file_info['rel_path'].split(os.sep)
        if len(parts) >= 3:
            client_folder = parts[2]  # inspection/2025/November/CLIENT_NAME/...
            if client_folder not in client_folders:
                client_folders[client_folder] = []
            client_folders[client_folder].append(file_info)

    # Display files grouped by client
    print("\nFILES TO BE DELETED:\n")
    for client, files in sorted(client_folders.items()):
        client_size = sum(f['size'] for f in files)
        print(f"[{client}] - {len(files)} files ({format_size(client_size)})")
        for f in files[:5]:  # Show first 5 files
            print(f"  - {f['rel_path']}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more files")
        print()

    # Save backup log
    log_file = f"deleted_new_clients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"FILES DELETED FOR CLIENTS STARTING WITH 'NEW'\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Total files: {len(files_to_delete)}\n")
        f.write(f"Total size: {format_size(total_size)}\n")
        f.write("="*100 + "\n\n")

        for client, files in sorted(client_folders.items()):
            f.write(f"\n[{client}] - {len(files)} files\n")
            f.write("-" * 100 + "\n")
            for file_info in files:
                f.write(f"  {file_info['rel_path']} ({format_size(file_info['size'])})\n")

    print(f"Backup log saved to: {log_file}\n")

    if dry_run:
        print("="*100)
        print("DRY RUN COMPLETE - No files were deleted")
        print(f"Run without --dry-run to actually delete files")
        print("="*100)
        return

    # Confirm deletion
    print("="*100)
    response = input("Are you sure you want to DELETE these files? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Deletion cancelled")
        return

    # Delete files
    print("\nDeleting files...")
    deleted_count = 0
    error_count = 0

    for file_info in files_to_delete:
        try:
            os.remove(file_info['path'])
            deleted_count += 1
            if deleted_count % 10 == 0:
                print(f"  Deleted {deleted_count}/{len(files_to_delete)} files...")
        except Exception as e:
            print(f"  ERROR deleting {file_info['rel_path']}: {e}")
            error_count += 1

    print(f"\nDeleted {deleted_count} files")
    if error_count > 0:
        print(f"Errors: {error_count} files could not be deleted")

    # Remove empty directories
    print("\nRemoving empty directories...")
    removed_dirs = 0
    for folder in sorted(folders_to_delete, reverse=True):  # Start from deepest folders
        try:
            if os.path.exists(folder) and not os.listdir(folder):
                os.rmdir(folder)
                removed_dirs += 1
        except Exception as e:
            pass  # Folder not empty or other error, skip

    print(f"Removed {removed_dirs} empty directories")

    print("\n" + "="*100)
    print("DELETION COMPLETE")
    print("="*100)
    print(f"Files deleted: {deleted_count}")
    print(f"Size freed: {format_size(total_size)}")
    print(f"Backup log: {log_file}")
    print("="*100)

def format_size(size_bytes):
    """Format bytes into human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv

    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage:")
        print("  python remove_new_client_files.py              # Delete files (with confirmation)")
        print("  python remove_new_client_files.py --dry-run    # Show what would be deleted")
        print("  python remove_new_client_files.py -d           # Same as --dry-run")
        sys.exit(0)

    remove_new_client_files('media', dry_run=dry_run)
