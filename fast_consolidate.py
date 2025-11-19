"""
Fast consolidation using parallel processing
"""

import os
import pickle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class FastDriveOrganizer:
    def __init__(self):
        self.creds = None
        self.drive = None
        self.token_path = 'token.pickle'
        self.lock = threading.Lock()

    def authenticate(self):
        """Authenticate using existing token.pickle"""
        print("Authenticating...")

        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        if not self.creds or not self.creds.valid:
            raise Exception("No valid credentials!")

        self.drive = build('drive', 'v3', credentials=self.creds)
        print("[OK] Authenticated\n")

    def list_folder_contents(self, folder_id):
        """List all items in a folder"""
        items = []
        page_token = None

        while True:
            response = self.drive.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields='nextPageToken, files(id, name, mimeType)',
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                corpora='allDrives',
                pageSize=1000
            ).execute()

            items.extend(response.get('files', []))
            page_token = response.get('nextPageToken')

            if not page_token:
                break

        return items

    def find_all_november_and_moved_folders(self, parent_folder_id):
        """Find all November 2025 folders AND November 2025 Moved files folders"""
        items = self.list_folder_contents(parent_folder_id)

        folders = [
            item for item in items
            if item['mimeType'] == 'application/vnd.google-apps.folder'
            and ('november' in item['name'].lower() and '2025' in item['name'])
        ]

        print(f"Found {len(folders)} November folders:")
        for folder in folders:
            print(f"  - {folder['name']} (ID: {folder['id']})")
        print()

        return folders

    def get_all_zip_files(self, folder_id):
        """Get all zip files recursively"""
        all_files = []
        folders_to_scan = [folder_id]

        while folders_to_scan:
            current = folders_to_scan.pop(0)
            items = self.list_folder_contents(current)

            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    folders_to_scan.append(item['id'])
                elif item['name'].endswith('.zip'):
                    all_files.append(item)

        return all_files

    def move_file_thread(self, file_info):
        """Move a single file (thread-safe)"""
        file_id = file_info['file_id']
        file_name = file_info['file_name']
        new_parent = file_info['new_parent']
        old_parent = file_info['old_parent']

        try:
            self.drive.files().update(
                fileId=file_id,
                addParents=new_parent,
                removeParents=old_parent,
                fields='id, parents',
                supportsAllDrives=True
            ).execute()
            return True, file_name
        except Exception as e:
            return False, f"{file_name}: {str(e)}"

    def create_folder(self, parent_id, folder_name):
        """Create a new folder"""
        print(f"Creating folder '{folder_name}'...")

        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }

        folder = self.drive.files().create(
            body=file_metadata,
            fields='id, name',
            supportsAllDrives=True
        ).execute()

        print(f"[OK] Created: {folder['name']} (ID: {folder['id']})\n")
        return folder

    def fast_consolidate(self, parent_folder_id, max_workers=10):
        """Fast consolidation using parallel processing"""
        print("="*70)
        print("FAST CONSOLIDATION - PARALLEL MODE")
        print("="*70 + "\n")

        # Find ALL November folders (including "Moved files" folders)
        all_folders = self.find_all_november_and_moved_folders(parent_folder_id)

        if not all_folders:
            print("No November folders found!")
            return

        # Check if "November 2025 FINAL" already exists
        final_folder = None
        for folder in all_folders:
            if folder['name'] == 'November 2025 FINAL':
                final_folder = folder
                print(f"Using existing folder: {final_folder['name']}\n")
                break

        if not final_folder:
            final_folder = self.create_folder(parent_folder_id, "November 2025 FINAL")

        # Collect all zip files from ALL folders
        print("Scanning all folders for zip files...")
        all_zip_files = []

        for folder in all_folders:
            if folder['id'] == final_folder['id']:
                continue

            print(f"  Scanning: {folder['name']}")
            zip_files = self.get_all_zip_files(folder['id'])

            for zip_file in zip_files:
                all_zip_files.append({
                    'file_id': zip_file['id'],
                    'file_name': zip_file['name'],
                    'new_parent': final_folder['id'],
                    'old_parent': folder['id']
                })

            print(f"    Found {len(zip_files)} files")

        print(f"\n{'='*70}")
        print(f"TOTAL: {len(all_zip_files)} files to move")
        print(f"{'='*70}\n")

        if not all_zip_files:
            print("No files to move!")
            return

        # Move files in parallel
        print(f"Moving files using {max_workers} parallel threads...\n")

        moved = 0
        failed_files = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.move_file_thread, file_info): file_info
                      for file_info in all_zip_files}

            for future in as_completed(futures):
                success, result = future.result()
                if success:
                    moved += 1
                    if moved % 100 == 0:
                        print(f"  Moved {moved}/{len(all_zip_files)} files...")
                else:
                    failed_files.append(result)

        # Retry failed files
        if failed_files:
            print(f"\n  Retrying {len(failed_files)} failed files...")
            retry_count = 0
            for failed in failed_files:
                file_name = failed.split(":")[0]
                file_info = next((f for f in all_zip_files if f['file_name'] == file_name), None)
                if file_info:
                    success, _ = self.move_file_thread(file_info)
                    if success:
                        moved += 1
                        retry_count += 1

            print(f"  Recovered {retry_count} files on retry")

        print(f"\n{'='*70}")
        print(f"COMPLETE!")
        print(f"{'='*70}")
        print(f"Moved: {moved}/{len(all_zip_files)}")
        print(f"Failed: {len(all_zip_files) - moved}")
        print(f"\nAll files are now in: {final_folder['name']}")
        print(f"Folder ID: {final_folder['id']}")


def main():
    PARENT_FOLDER_ID = '1pzot8MQ-m3u0f9-BWxpBO40QgLmeZhRP'

    organizer = FastDriveOrganizer()

    try:
        organizer.authenticate()
        organizer.fast_consolidate(PARENT_FOLDER_ID, max_workers=10)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
