#!/usr/bin/env python3
"""
Script to fix misplaced folders that were moved to the wrong level.
Move folders from month level back to their correct client directories.
"""

import os
import shutil
from pathlib import Path

def fix_september_folders():
    """Fix the misplaced folders in September 2025."""
    september_path = os.path.join('media', 'inspection', '2025', 'September')
    
    if not os.path.exists(september_path):
        print(f"❌ September path not found: {september_path}")
        return
    
    print(f"🔍 Fixing misplaced folders in: {september_path}")
    
    # Folders that should be moved back to client directories
    misplaced_folders = [
        'Compliance',
        'inspection-0402',
        'inspection-0652', 
        'inspection-0907',
        'inspection-0968',
        'inspection-1209',
        'inspection-3518',
        'inspection-3657',
        'inspection-4154',
        'inspection-4641',
        'invoice',
        'rfi'
    ]
    
    # Get list of client directories
    client_dirs = []
    for item in os.listdir(september_path):
        item_path = os.path.join(september_path, item)
        if os.path.isdir(item_path) and not item.startswith('inspection-') and item not in ['Compliance', 'invoice', 'rfi']:
            client_dirs.append(item)
    
    print(f"📁 Found client directories: {client_dirs}")
    print(f"📦 Found misplaced folders: {misplaced_folders}")
    
    # Move misplaced folders to appropriate client directories
    for folder in misplaced_folders:
        folder_path = os.path.join(september_path, folder)
        
        if not os.path.exists(folder_path):
            print(f"  ⚠️ Folder {folder} not found, skipping...")
            continue
        
        print(f"  🔍 Processing {folder}...")
        
        if folder == 'Compliance':
            # Move Compliance folder to all client directories that don't have one
            for client in client_dirs:
                client_path = os.path.join(september_path, client)
                dest_path = os.path.join(client_path, 'Compliance')
                
                if not os.path.exists(dest_path):
                    # Move the entire Compliance folder to this client
                    shutil.move(folder_path, dest_path)
                    print(f"    ✅ Moved Compliance to {client}")
                    break
                else:
                    # Merge contents
                    print(f"    🔄 Merging Compliance with existing folder in {client}")
                    for item in os.listdir(folder_path):
                        src = os.path.join(folder_path, item)
                        dst = os.path.join(dest_path, item)
                        if os.path.exists(dst):
                            os.remove(dst)
                        shutil.move(src, dst)
                    os.rmdir(folder_path)
                    print(f"    ✅ Merged Compliance into {client}")
                    break
        
        elif folder.startswith('inspection-'):
            # Move inspection folders to appropriate client directories
            # We need to determine which client this inspection belongs to
            # For now, let's move them to the first client that doesn't have this inspection
            for client in client_dirs:
                client_path = os.path.join(september_path, client)
                dest_path = os.path.join(client_path, folder)
                
                if not os.path.exists(dest_path):
                    shutil.move(folder_path, dest_path)
                    print(f"    ✅ Moved {folder} to {client}")
                    break
        
        elif folder in ['invoice', 'rfi']:
            # Move invoice/rfi folders to all client directories that don't have one
            for client in client_dirs:
                client_path = os.path.join(september_path, client)
                dest_path = os.path.join(client_path, folder)
                
                if not os.path.exists(dest_path):
                    shutil.move(folder_path, dest_path)
                    print(f"    ✅ Moved {folder} to {client}")
                    break
                else:
                    # Merge contents
                    print(f"    🔄 Merging {folder} with existing folder in {client}")
                    for item in os.listdir(folder_path):
                        src = os.path.join(folder_path, item)
                        dst = os.path.join(dest_path, item)
                        if os.path.exists(dst):
                            os.remove(dst)
                        shutil.move(src, dst)
                    os.rmdir(folder_path)
                    print(f"    ✅ Merged {folder} into {client}")
                    break

if __name__ == "__main__":
    fix_september_folders()
    print("✅ Folder fix complete!")
