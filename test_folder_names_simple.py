#!/usr/bin/env python3
"""
Test script to debug folder name handling for clients with forward slashes
"""
import os
import re
from datetime import datetime

def create_folder_name(name):
    """Use original client name for folder names, but replace forward slashes with spaces"""
    if not name:
        return "Unknown Client"
    # Replace forward slashes with spaces (since / cannot be used in folder names)
    # This handles cases like "T/A" becoming "T A"
    return name.replace('/', ' ').strip()

def sanitize_client_name(client_name):
    """Sanitize client name to match folder structure (same as upload_document)"""
    sanitized_client_name = re.sub(r'[^a-zA-Z0-9_]', '_', client_name)
    sanitized_client_name = re.sub(r'_+', '_', sanitized_client_name).strip('_')
    return sanitized_client_name

def test_client_name_handling():
    """Test how client names are handled"""
    test_clients = [
        "Great Octave Trading 513 CC T/A Sun African",
        "Marang Layers Farming Enterprises t/a Maranga Eggs",
        "Pick 'n Pay - Bt Ngebs Mthatha",
        "Fairfield Meat Center Parow"
    ]
    
    print("=== CLIENT NAME HANDLING TEST ===")
    print()
    
    for client_name in test_clients:
        print(f"Original client name: '{client_name}'")
        
        # Method 1: create_folder_name (used in upload)
        folder_name = create_folder_name(client_name)
        print(f"  Folder name (upload):     '{folder_name}'")
        
        # Method 2: sanitize_client_name (used in file detection)
        sanitized_name = sanitize_client_name(client_name)
        print(f"  Sanitized name (detect):  '{sanitized_name}'")
        
        # Method 3: name with spaces for slash (new detection method)
        name_with_spaces = client_name.replace('/', ' ')
        print(f"  Name with spaces:         '{name_with_spaces}'")
        
        # Check if they match
        match_folder_sanitized = (folder_name == sanitized_name)
        match_folder_spaces = (folder_name == name_with_spaces)
        
        print(f"  Folder == Sanitized:      {match_folder_sanitized}")
        print(f"  Folder == Spaces:         {match_folder_spaces}")
        
        if not match_folder_sanitized and not match_folder_spaces:
            print(f"  X MISMATCH! Upload creates '{folder_name}' but detection looks for '{sanitized_name}'")
        else:
            print(f"  OK MATCH! Detection will find the folder")
        
        print()

def test_file_path_simulation():
    """Simulate the actual file paths that would be created"""
    client_name = "Great Octave Trading 513 CC T/A Sun African"
    inspection_date = "2025-09-23"
    
    print("=== FILE PATH SIMULATION ===")
    print(f"Client: {client_name}")
    print(f"Date: {inspection_date}")
    print()
    
    # Parse date
    date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
    year_folder = date_obj.strftime('%Y')
    month_folder = date_obj.strftime('%B')
    
    print(f"Year folder: {year_folder}")
    print(f"Month folder: {month_folder}")
    print()
    
    # Upload path (what gets created)
    folder_name = create_folder_name(client_name)
    upload_path = f"media/inspection/{year_folder}/{month_folder}/{folder_name}/rfi/"
    print(f"Upload creates folder: {upload_path}")
    print()
    
    # Detection paths (what gets searched)
    sanitized_name = sanitize_client_name(client_name)
    name_with_spaces = client_name.replace('/', ' ')
    
    detection_paths = [
        f"media/inspection/{year_folder}/{month_folder}/{sanitized_name}/",
        f"media/inspection/{year_folder}/{month_folder}/{client_name}/",
        f"media/inspection/{year_folder}/{month_folder}/{name_with_spaces}/"
    ]
    
    print("Detection searches for:")
    for i, path in enumerate(detection_paths, 1):
        print(f"  {i}. {path}")
        match = (path.replace('/', '').replace(' ', '') == upload_path.replace('/', '').replace(' ', '').replace('rfi', ''))
        print(f"     Matches upload: {match}")
    
    print()

if __name__ == "__main__":
    test_client_name_handling()
    test_file_path_simulation()
    
    print("=== RECOMMENDATION ===")
    print("The upload function should use the SAME naming logic as detection!")
    print("Both should use: client_name.replace('/', ' ') for consistency")
