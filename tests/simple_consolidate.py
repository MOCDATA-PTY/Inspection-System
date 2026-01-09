"""
Simple sequential consolidation - more reliable
"""

import os
import pickle
import time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class SimpleDriveOrganizer:
    def __init__(self):
        self.creds = None
        self.drive = None
        self.token_path = 'token.pickle'

    def authenticate(self):
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

    def find_november_folders(self, parent_folder_id):
        items = self.list_folder_contents(parent_folder_id)
        folders = [
            item for item in items
            if item['mimeType'] == 'application/vnd.google-apps.folder'
            and ('november' in item['name'].lower() and '2025' in item['name'])
        ]
        return folders

    def get_all_zip_files(self, folder_id):
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

    def create_folder(self, parent_id, folder_name):
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

        print(f"Created: {folder['name']} (ID: {folder['id']})\n")
        return folder

    def move_file(self, file_id, file_name, new_parent, old_parent):
        try:
            self.drive.files().update(
                fileId=file_id,
                addParents=new_parent,
                removeParents=old_parent,
                fields='id',
                supportsAllDrives=True
            ).execute()
            return True
        except Exception as e:
            print(f"  ERROR: {file_name}: {e}")
            return False

    def consolidate(self, parent_folder_id):
        print("="*70)
        print("SIMPLE CONSOLIDATION")
        print("="*70 + "\n")

        # Find all November folders
        all_folders = self.find_november_folders(parent_folder_id)
        print(f"Found {len(all_folders)} November folders\n")

        # Check for existing FINAL folder
        final_folder = None
        for folder in all_folders:
            if folder['name'] == 'November 2025 FINAL':
                final_folder = folder
                print(f"Using: {final_folder['name']}\n")
                break

        if not final_folder:
            final_folder = self.create_folder(parent_folder_id, "November 2025 FINAL")

        # Collect all zip files
        print("Scanning for zip files...\n")
        all_files = []

        for folder in all_folders:
            if folder['id'] == final_folder['id']:
                continue

            print(f"Scanning: {folder['name']}")
            zip_files = self.get_all_zip_files(folder['id'])
            print(f"  Found {len(zip_files)} files")

            for zf in zip_files:
                all_files.append({
                    'file_id': zf['id'],
                    'file_name': zf['name'],
                    'source_folder_id': folder['id']
                })

        print(f"\nTOTAL: {len(all_files)} files to move\n")
        print("="*70)
        print("MOVING FILES (this will take a few minutes)")
        print("="*70 + "\n")

        # Move files sequentially
        moved = 0
        failed = 0

        for i, file_info in enumerate(all_files, 1):
            success = self.move_file(
                file_info['file_id'],
                file_info['file_name'],
                final_folder['id'],
                file_info['source_folder_id']
            )

            if success:
                moved += 1
            else:
                failed += 1

            # Progress update every 50 files
            if i % 50 == 0:
                print(f"Progress: {i}/{len(all_files)} ({moved} moved, {failed} failed)")

            # Small delay to avoid rate limiting
            time.sleep(0.1)

        print(f"\n{'='*70}")
        print(f"COMPLETE!")
        print(f"{'='*70}")
        print(f"Moved: {moved}/{len(all_files)}")
        print(f"Failed: {failed}")
        print(f"\nAll files in: {final_folder['name']}")
        print(f"ID: {final_folder['id']}")


def main():
    PARENT_FOLDER_ID = '1pzot8MQ-m3u0f9-BWxpBO40QgLmeZhRP'

    organizer = SimpleDriveOrganizer()

    try:
        organizer.authenticate()
        organizer.consolidate(PARENT_FOLDER_ID)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
