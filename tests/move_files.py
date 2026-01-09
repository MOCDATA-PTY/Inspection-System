"""
Organize Google Drive compliance documents into month folders
Moves files into folders like "October 2025", "September 2025" based on filename dates
"""

import os
import pickle
import re
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Google Drive settings
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token_drive.pickle'  # Use existing Drive token
CREDENTIALS_PATH = 'credentials.json'
SOURCE_FOLDER_ID = '18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4'  # The folder with all the files

def authenticate():
    """Authenticate with Google Drive API."""
    print("[Auth] Authenticating with Google Drive...")
    creds = None

    # Load existing token
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[Auth] Refreshing token...")
            creds.refresh(Request())
        else:
            print("[Auth] Getting new authorization...")
            flow = Flow.from_client_secrets_file(
                CREDENTIALS_PATH,
                SCOPES,
                redirect_uri='http://127.0.0.1:8000/google-sheets/oauth2callback/'
            )
            auth_url, _ = flow.authorization_url(
                prompt='consent',
                access_type='offline',
                include_granted_scopes='true'
            )
            print(f'\n[Auth] Please visit this URL to authorize:\n{auth_url}\n')
            code = input('Enter the authorization code: ').strip()

            # Fetch token without strict scope checking
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', message='.*Scope has changed.*')
                flow.fetch_token(code=code)

            creds = flow.credentials

        # Save credentials
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    print("[Auth] Authentication successful!")
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, folder_name, parent_folder_id):
    """Get existing folder ID or create new folder."""
    # Search for existing folder
    query = f"name='{folder_name}' and '{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        q=query,
        fields='files(id, name)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()

    files = results.get('files', [])

    if files:
        return files[0]['id']

    # Create new folder
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }

    folder = service.files().create(
        body=file_metadata,
        fields='id',
        supportsAllDrives=True
    ).execute()

    print(f"[Created] Folder: {folder_name}")
    return folder.get('id')

def extract_date_from_filename(filename):
    """Extract date from compliance document filename."""
    # Pattern: COMMODITY-...-YYYY-MM-DD.zip
    pattern = r'(\d{4}-\d{2}-\d{2})'
    match = re.search(pattern, filename)

    if match:
        date_str = match.group(1)
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj
        except:
            return None
    return None

def move_file_to_folder(service, file_id, file_name, target_folder_id, source_folder_id):
    """Move file to target folder."""
    try:
        # Remove file from source folder and add to target folder
        service.files().update(
            fileId=file_id,
            addParents=target_folder_id,
            removeParents=source_folder_id,
            fields='id, parents',
            supportsAllDrives=True
        ).execute()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to move {file_name}: {e}")
        return False

def organize_files_by_month(dry_run=False, max_files=None):
    """Main function to organize files into month folders."""
    print("=" * 80)
    print("GOOGLE DRIVE FILE ORGANIZER - Organize by Month")
    if dry_run:
        print("*** DRY RUN MODE - No files will be moved ***")
    print("=" * 80)
    print()

    # Authenticate
    service = authenticate()
    print()

    # Get all files from source folder
    print(f"[Fetching] Loading files from source folder...")
    print(f"[Folder ID] {SOURCE_FOLDER_ID}")
    if max_files:
        print(f"[Limit] Will process maximum {max_files} files")
    print()

    all_files = []
    page_token = None
    page_count = 0

    while True:
        page_count += 1

        # Show progress every 10 pages
        if page_count % 10 == 0:
            print(f"[Progress] Fetching page {page_count}... (total so far: {len(all_files)})")

        query = f"'{SOURCE_FOLDER_ID}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'"
        results = service.files().list(
            q=query,
            pageSize=1000,
            fields='nextPageToken, files(id, name, parents)',
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()

        files = results.get('files', [])
        all_files.extend(files)

        # Show every 50 pages or every 50k files
        if page_count % 50 == 0 or len(all_files) % 50000 == 0:
            print(f"[Progress] Page {page_count} | Total files: {len(all_files)}")

        # Check if we hit max limit
        if max_files and len(all_files) >= max_files:
            print(f"[Limit] Reached maximum of {max_files} files, stopping fetch")
            all_files = all_files[:max_files]
            break

        page_token = results.get('nextPageToken')
        if not page_token:
            break

    print()
    print(f"[Total] Found {len(all_files)} files to organize")
    print()

    # Group files by month
    files_by_month = {}
    skipped_files = []

    for file in all_files:
        file_name = file.get('name', '')
        date_obj = extract_date_from_filename(file_name)

        if date_obj:
            month_key = date_obj.strftime('%B %Y')  # e.g., "October 2025"
            if month_key not in files_by_month:
                files_by_month[month_key] = []
            files_by_month[month_key].append(file)
        else:
            skipped_files.append(file_name)

    print(f"[Organized] Files grouped into {len(files_by_month)} months")
    print(f"[Skipped] {len(skipped_files)} files without valid dates")
    print()

    if skipped_files:
        print("[Skipped Files]")
        for name in skipped_files[:10]:  # Show first 10
            print(f"  - {name}")
        if len(skipped_files) > 10:
            print(f"  ... and {len(skipped_files) - 10} more")
        print()

    # Create folders and move files
    print("=" * 80)
    print("MOVING FILES TO MONTH FOLDERS")
    print("=" * 80)
    print()

    month_folders = {}
    total_moved = 0
    total_failed = 0

    for month_name in sorted(files_by_month.keys()):
        files_in_month = files_by_month[month_name]
        print(f"\n[Month] {month_name} - {len(files_in_month)} files")

        # Get or create month folder
        folder_id = get_or_create_folder(service, month_name, SOURCE_FOLDER_ID)
        month_folders[month_name] = folder_id

        # Move files
        moved_count = 0
        for i, file in enumerate(files_in_month, 1):
            file_id = file['id']
            file_name = file['name']

            # Show progress every 10 files or at the end
            if i % 10 == 0 or i == len(files_in_month):
                print(f"  [Progress] {i}/{len(files_in_month)} files...", end='\r')

            success = move_file_to_folder(service, file_id, file_name, folder_id, SOURCE_FOLDER_ID)

            if success:
                moved_count += 1
                total_moved += 1
            else:
                total_failed += 1

        print(f"  [Completed] Moved {moved_count}/{len(files_in_month)} files")

    # Summary
    print()
    print("=" * 80)
    print("ORGANIZATION COMPLETE")
    print("=" * 80)
    print(f"Total files processed: {len(all_files)}")
    print(f"Successfully moved: {total_moved}")
    print(f"Failed: {total_failed}")
    print(f"Skipped (no date): {len(skipped_files)}")
    print(f"Months created: {len(month_folders)}")
    print()
    print("Month folders:")
    for month_name in sorted(month_folders.keys()):
        file_count = len(files_by_month[month_name])
        print(f"  - {month_name}: {file_count} files")
    print()
    print(f"[Drive URL] https://drive.google.com/drive/folders/{SOURCE_FOLDER_ID}")
    print("=" * 80)

if __name__ == "__main__":
    try:
        organize_files_by_month()
    except KeyboardInterrupt:
        print("\n\n[Cancelled] Organization stopped by user")
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
