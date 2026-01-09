#!/usr/bin/env python3
"""
Apply Partial Matching Fix for Client Names with "/" Characters
================================================================
This script updates core_views.py to handle client names with "/" that create nested folders.

Run on the server:
    python3 apply_partial_matching_fix.py
"""

import os
import sys
import shutil
from datetime import datetime

# Path to the file to update
FILE_PATH = '/root/Inspection-System/main/views/core_views.py'

# Backup suffix
BACKUP_SUFFIX = f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'

def create_backup():
    """Create a backup of the original file."""
    backup_path = FILE_PATH + BACKUP_SUFFIX
    shutil.copy2(FILE_PATH, backup_path)
    print(f"✓ Created backup: {backup_path}")
    return backup_path

def read_file():
    """Read the current file content."""
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(content):
    """Write updated content to file."""
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Updated: {FILE_PATH}")

def apply_fix_1(content):
    """Apply fix to get_inspection_files_local() function."""

    # Find the section to replace (lines 8940-8975)
    old_code = '''        # Try original client name first (as stored in database with spaces)
        client_base_path = os.path.join(base_inspection_path, client_name)

        # If original name doesn't exist, try converted name (with underscores/lowercase)
        if not os.path.exists(client_base_path):
            client_base_path = os.path.join(base_inspection_path, client_folder)'''

    new_code = '''        # Try to find client folder - check both exact and partial matches
        # Problem: sanitized folders may exist but be empty, while the actual files
        # are in folders with "/" that created nested directories
        candidate_folders = []

        # Try exact matches first
        for variation in [client_name, client_folder]:
            test_path = os.path.join(base_inspection_path, variation)
            if os.path.exists(test_path):
                candidate_folders.append(test_path)
                print(f"[DEBUG get_inspection_files_local] Found exact match candidate: {variation}")

        # Also try partial matching (for client names with "/" that create nested dirs)
        if os.path.exists(base_inspection_path):
            try:
                available_folders = [f for f in os.listdir(base_inspection_path) if os.path.isdir(os.path.join(base_inspection_path, f))]
                print(f"[DEBUG get_inspection_files_local] Searching in {len(available_folders)} available folders")

                for available_folder in available_folders:
                    for variation in [client_name, client_folder]:
                        # Get the part before any "/" or special char
                        variation_prefix = variation.split('/')[0].strip()

                        # Normalize for comparison
                        normalized_available = available_folder.lower().replace('_', ' ').strip()
                        normalized_prefix = variation_prefix.lower().replace('_', ' ').strip()

                        # Check if the available folder starts with the variation prefix
                        if normalized_available.startswith(normalized_prefix) and len(normalized_prefix) > 10:
                            candidate_path = os.path.join(base_inspection_path, available_folder)
                            if candidate_path not in candidate_folders:
                                candidate_folders.append(candidate_path)
                                print(f"[DEBUG get_inspection_files_local] Found partial match candidate: {available_folder}")
                            break
            except Exception as e:
                print(f"[DEBUG get_inspection_files_local] Error finding partial matches: {e}")

        # Now check which candidate has actual Inspection folders
        client_base_path = None
        for candidate in candidate_folders:
            # Quick check: does this folder have any Inspection-XXX subfolders?
            has_inspection_folders = False
            try:
                for item in os.listdir(candidate):
                    item_path = os.path.join(candidate, item)
                    # Check direct Inspection folders
                    if item.lower().startswith('inspection-') and os.path.isdir(item_path):
                        has_inspection_folders = True
                        print(f"[DEBUG get_inspection_files_local] Found Inspection folder: {item}")
                        break
                    # Also check DATE subfolders (new structure)
                    if os.path.isdir(item_path) and not item.lower().startswith('inspection-'):
                        try:
                            for subitem in os.listdir(item_path):
                                if subitem.lower().startswith('inspection-'):
                                    has_inspection_folders = True
                                    print(f"[DEBUG get_inspection_files_local] Found Inspection folder in {item}: {subitem}")
                                    break
                        except:
                            pass
                    if has_inspection_folders:
                        break
            except Exception as e:
                print(f"[DEBUG get_inspection_files_local] Error checking {candidate}: {e}")

            if has_inspection_folders:
                client_base_path = candidate
                print(f"[DEBUG get_inspection_files_local] Selected folder with Inspection folders: {client_base_path}")
                break

        # If no folder with files found, use the first candidate (or None)
        if not client_base_path:
            if candidate_folders:
                client_base_path = candidate_folders[0]
                print(f"[DEBUG get_inspection_files_local] No Inspection folders found, using first candidate: {client_base_path}")
            else:
                client_base_path = os.path.join(base_inspection_path, client_name)
                print(f"[DEBUG get_inspection_files_local] No candidates found, using default: {client_base_path}")'''

    if old_code in content:
        content = content.replace(old_code, new_code)
        print("✓ Applied Fix 1: get_inspection_files_local() partial matching")
        return content, True
    else:
        print("✗ Fix 1: Pattern not found (may already be applied)")
        return content, False

def apply_fix_2(content):
    """Apply fix to list_client_folder_files() function."""

    # Find the section to replace
    old_code = '''        # Check all folder variations for files
        for folder_variation in client_folder_variations:
            test_path = os.path.join(parent_path, folder_variation)
            if not os.path.exists(test_path):
                continue

            print(f"[DEBUG] Checking folder: {test_path}")'''

    new_code = '''        # Find all matching folders (exact and partial matches for nested "/" structures)
        matched_folders = []

        # First try exact matches
        for folder_variation in client_folder_variations:
            test_path = os.path.join(parent_path, folder_variation)
            if os.path.exists(test_path):
                matched_folders.append((test_path, folder_variation))
                print(f"[DEBUG] Found exact match: {folder_variation}")

        # If no exact match found, try partial matching (for client names with "/" that create nested dirs)
        if not matched_folders and os.path.exists(parent_path):
            try:
                print(f"[DEBUG] No exact match found, trying partial matching in: {parent_path}")
                # List all folders in parent_path
                available_folders = [f for f in os.listdir(parent_path) if os.path.isdir(os.path.join(parent_path, f))]
                print(f"[DEBUG] Available folders: {available_folders[:10]}")  # Show first 10

                # Try to find folders that partially match the client name
                for available_folder in available_folders:
                    # Check if this folder is a partial match (for names split by "/" like "t/a")
                    for folder_variation in client_folder_variations:
                        # Get the part before any "/" or special char
                        variation_prefix = folder_variation.split('/')[0].strip()

                        # Normalize for comparison (case insensitive, ignore underscores)
                        normalized_available = available_folder.lower().replace('_', ' ').strip()
                        normalized_prefix = variation_prefix.lower().replace('_', ' ').strip()

                        # Check if the available folder starts with the variation prefix
                        # This handles cases like "Marang Layers Farming Enterprises t/" matching "Marang Layers Farming Enterprises t/a..."
                        if normalized_available.startswith(normalized_prefix) and len(normalized_prefix) > 10:
                            potential_path = os.path.join(parent_path, available_folder)
                            matched_folders.append((potential_path, available_folder))
                            print(f"[DEBUG] Found partial match: {available_folder} for {folder_variation}")
                            break  # Found a match for this available folder, move to next
            except Exception as e:
                print(f"[DEBUG] Error during partial matching: {e}")

        print(f"[DEBUG] Total matched folders: {len(matched_folders)}")

        # Process all matched folders (both exact and partial matches)
        for test_path, folder_name in matched_folders:
            print(f"[DEBUG] Checking folder: {test_path}")'''

    if old_code in content:
        content = content.replace(old_code, new_code)
        print("✓ Applied Fix 2: list_client_folder_files() partial matching")
        return content, True
    else:
        print("✗ Fix 2: Pattern not found (may already be applied)")
        return content, False

def main():
    """Main function."""
    print("="*70)
    print("Applying Partial Matching Fix for Client Names with '/'")
    print("="*70)
    print()

    # Check if file exists
    if not os.path.exists(FILE_PATH):
        print(f"✗ Error: File not found: {FILE_PATH}")
        return 1

    # Create backup
    backup_path = create_backup()

    # Read current content
    print("Reading file...")
    content = read_file()

    # Apply fixes
    print("\nApplying fixes...")
    content, fix1_applied = apply_fix_1(content)
    content, fix2_applied = apply_fix_2(content)

    # Write updated content if any fixes were applied
    if fix1_applied or fix2_applied:
        write_file(content)
        print("\n" + "="*70)
        print("SUCCESS! Fixes applied.")
        print("="*70)
        print("\nNext steps:")
        print("  1. Restart the service: sudo systemctl restart inspection-system")
        print("  2. Test with: Marang Layers Farming Enterprises t/a Maranga Eggs (Date: 2025-10-01)")
        print(f"  3. If something goes wrong, restore from: {backup_path}")
        return 0
    else:
        print("\n" + "="*70)
        print("No fixes applied - patterns not found or already applied")
        print("="*70)
        return 1

if __name__ == '__main__':
    sys.exit(main())
