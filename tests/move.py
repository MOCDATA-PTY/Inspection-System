"""
Move zip files from source folder to organized folders based on date in filename.
Source: https://drive.google.com/drive/folders/18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4
Destination: https://drive.google.com/drive/folders/1Q8ZXVC2NhzrPpDCdwfHGt8o726fLtqE_
"""

import os
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
import pickle

# Folder IDs extracted from URLs
SOURCE_FOLDER_ID = '18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4'  # Zip Folder
DESTINATION_FOLDER_ID = '1Q8ZXVC2NhzrPpDCdwfHGt8o726fLtqE_'  # Organized Files

def get_drive_service():
    """Authenticate and return Google Drive service."""
    creds = None

    # Load credentials from token.pickle
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If credentials are invalid or don't exist, need to authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save the refreshed credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        else:
            print("Error: No valid credentials found. Please run authentication first.")
            return None

    service = build('drive', 'v3', credentials=creds)
    return service

def parse_date_from_filename(filename):
    """
    Extract date from filename in format like:
    Egg-RE-IND-EGG-NA-4651-2025-09-16.zip -> September 2025

    Returns tuple: (month_name, year) or None if no date found
    """
    # Pattern to match YYYY-MM-DD format in filename
    pattern = r'(\d{4})-(\d{2})-\d{2}'
    match = re.search(pattern, filename)

    if match:
        year = match.group(1)
        month = match.group(2)

        # Convert month number to month name
        month_names = {
            '01': 'January', '02': 'February', '03': 'March', '04': 'April',
            '05': 'May', '06': 'June', '07': 'July', '08': 'August',
            '09': 'September', '10': 'October', '11': 'November', '12': 'December'
        }

        month_name = month_names.get(month, None)
        if month_name:
            return (month_name, year)

    return None

def get_or_create_folder(service, folder_name, parent_id):
    """Get folder ID if exists, otherwise create it."""
    try:
        # Search for existing folder (works with shared drives)
        query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            corpora='allDrives'
        ).execute()

        files = response.get('files', [])

        if files:
            print(f"  Found existing folder: {folder_name}")
            return files[0]['id']

        # Create folder if it doesn't exist
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }

        folder = service.files().create(
            body=file_metadata,
            fields='id',
            supportsAllDrives=True
        ).execute()

        print(f"  Created new folder: {folder_name}")
        return folder.get('id')

    except HttpError as error:
        print(f"Error creating/getting folder {folder_name}: {error}")
        return None

def move_file(service, file_id, new_parent_id, old_parent_id):
    """Move a file to a new parent folder."""
    try:
        # Retrieve the existing parents to remove
        file = service.files().get(
            fileId=file_id,
            fields='parents',
            supportsAllDrives=True
        ).execute()

        previous_parents = ",".join(file.get('parents', []))

        # Move the file to the new folder
        file = service.files().update(
            fileId=file_id,
            addParents=new_parent_id,
            removeParents=previous_parents,
            fields='id, parents',
            supportsAllDrives=True
        ).execute()

        return True

    except HttpError as error:
        print(f"  Error moving file: {error}")
        return False

def organize_zip_files():
    """Main function to organize zip files by date."""
    service = get_drive_service()
    if not service:
        return

    print("Starting file organization...")
    print(f"Source folder: {SOURCE_FOLDER_ID}")
    print(f"Destination folder: {DESTINATION_FOLDER_ID}")
    print("-" * 60)

    try:
        # Get all zip files from source folder (works with shared drives)
        # Handle pagination to get ALL files
        query = f"'{SOURCE_FOLDER_ID}' in parents and trashed=false and (mimeType='application/zip' or mimeType='application/x-zip-compressed' or name contains 'zip')"

        print("Fetching file list (this may take a moment for large folders)...")
        files = []
        page_token = None

        while True:
            response = service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType)',
                pageSize=1000,
                pageToken=page_token,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                corpora='allDrives'
            ).execute()

            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken')

            print(f"  Fetched {len(files)} files so far...")

            if not page_token:
                break

        if not files:
            print("No zip files found in source folder.")
            return

        print(f"Found {len(files)} zip files to organize.\n")

        moved_count = 0
        skipped_count = 0
        total_files = len(files)

        for index, file in enumerate(files, 1):
            file_name = file['name']
            file_id = file['id']

            print(f"\n[{index}/{total_files}] Processing: {file_name}")

            # Parse date from filename
            date_info = parse_date_from_filename(file_name)

            if not date_info:
                print(f"  Skipped - couldn't parse date from filename")
                skipped_count += 1
                continue

            month_name, year = date_info

            # Get or create year folder
            year_folder_id = get_or_create_folder(service, year, DESTINATION_FOLDER_ID)
            if not year_folder_id:
                print(f"  Skipped - couldn't create year folder")
                skipped_count += 1
                continue

            # Get or create month folder inside year folder
            month_folder_name = f"{month_name} {year}"
            month_folder_id = get_or_create_folder(service, month_folder_name, year_folder_id)
            if not month_folder_id:
                print(f"  Skipped - couldn't create month folder")
                skipped_count += 1
                continue

            # Move file to month folder
            if move_file(service, file_id, month_folder_id, SOURCE_FOLDER_ID):
                print(f"  [OK] Moved to: {year}/{month_folder_name}")
                moved_count += 1
                print(f"  Progress: {moved_count} moved, {skipped_count} skipped")
            else:
                print(f"  [FAIL] Failed to move file")
                skipped_count += 1

        print("-" * 60)
        print(f"Organization complete!")
        print(f"Moved: {moved_count} files")
        print(f"Skipped: {skipped_count} files")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    organize_zip_files()
