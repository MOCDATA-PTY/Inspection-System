#!/usr/bin/env python3
"""
Script to fix the folder structure by moving misplaced folders back to client directories.
"""

import os
import shutil

def fix_folder_structure():
    """Fix the misplaced folder structure."""
    september_path = os.path.join('media', 'inspection', '2025', 'September')
    
    print(f"🔍 Fixing folder structure in: {september_path}")
    
    # Get all client directories
    client_dirs = []
    misplaced_folders = []
    
    for item in os.listdir(september_path):
        item_path = os.path.join(september_path, item)
        if os.path.isdir(item_path):
            if item.startswith('inspection-') or item in ['Compliance', 'invoice', 'rfi']:
                misplaced_folders.append(item)
            else:
                client_dirs.append(item)
    
    print(f"📁 Client directories: {client_dirs}")
    print(f"📦 Misplaced folders: {misplaced_folders}")
    
    # Move inspection folders to Amakhosi Chickens (inspection-0402 belongs there)
    if 'Amakhosi Chickens' in client_dirs:
        amakhosi_path = os.path.join(september_path, 'Amakhosi Chickens')
        
        # Move inspection-0402
        if 'inspection-0402' in misplaced_folders:
            src = os.path.join(september_path, 'inspection-0402')
            dst = os.path.join(amakhosi_path, 'inspection-0402')
            if not os.path.exists(dst):
                shutil.move(src, dst)
                print(f"✅ Moved inspection-0402 to Amakhosi Chickens")
                misplaced_folders.remove('inspection-0402')
    
    # Move invoice and rfi folders to all client directories
    for folder_type in ['invoice', 'rfi']:
        if folder_type in misplaced_folders:
            src = os.path.join(september_path, folder_type)
            
            # Move to first client that doesn't have this folder
            for client in client_dirs:
                client_path = os.path.join(september_path, client)
                dst = os.path.join(client_path, folder_type)
                
                if not os.path.exists(dst):
                    shutil.move(src, dst)
                    print(f"✅ Moved {folder_type} to {client}")
                    misplaced_folders.remove(folder_type)
                    break
                else:
                    # Merge contents
                    print(f"🔄 Merging {folder_type} with existing folder in {client}")
                    for item in os.listdir(src):
                        item_src = os.path.join(src, item)
                        item_dst = os.path.join(dst, item)
                        if os.path.exists(item_dst):
                            os.remove(item_dst)
                        shutil.move(item_src, item_dst)
                    os.rmdir(src)
                    print(f"✅ Merged {folder_type} into {client}")
                    misplaced_folders.remove(folder_type)
                    break
    
    # Move Compliance folder to all client directories that don't have one
    if 'Compliance' in misplaced_folders:
        src = os.path.join(september_path, 'Compliance')
        
        for client in client_dirs:
            client_path = os.path.join(september_path, client)
            dst = os.path.join(client_path, 'Compliance')
            
            if not os.path.exists(dst):
                shutil.move(src, dst)
                print(f"✅ Moved Compliance to {client}")
                misplaced_folders.remove('Compliance')
                break
            else:
                # Merge contents
                print(f"🔄 Merging Compliance with existing folder in {client}")
                for item in os.listdir(src):
                    item_src = os.path.join(src, item)
                    item_dst = os.path.join(dst, item)
                    if os.path.exists(item_dst):
                        os.remove(item_dst)
                    shutil.move(item_src, item_dst)
                os.rmdir(src)
                print(f"✅ Merged Compliance into {client}")
                misplaced_folders.remove('Compliance')
                break
    
    # Handle remaining inspection folders - distribute them to clients
    remaining_inspections = [f for f in misplaced_folders if f.startswith('inspection-')]
    for inspection in remaining_inspections:
        src = os.path.join(september_path, inspection)
        
        # Move to first client that doesn't have this inspection
        for client in client_dirs:
            client_path = os.path.join(september_path, client)
            dst = os.path.join(client_path, inspection)
            
            if not os.path.exists(dst):
                shutil.move(src, dst)
                print(f"✅ Moved {inspection} to {client}")
                break
    
    print(f"✅ Folder structure fix complete!")

if __name__ == "__main__":
    fix_folder_structure()
