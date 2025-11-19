"""
Consolidate multiple 'November 2025' folders into a single folder with all zip files
"""

import os
import pickle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class DriveOrganizer:
    def __init__(self):
        self.creds = None
        self.drive = None
        self.token_path = 'token.pickle'

    def authenticate(self):
        """Authenticate using existing token.pickle"""
        print("Authenticating with Google Drive...")

        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # Refresh if expired
        if self.creds and self.creds.expired and self.creds.refresh_token:
            print("Refreshing expired token...")
            self.creds.refresh(Request())
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        if not self.creds or not self.creds.valid:
            raise Exception("No valid credentials found. Please re-authenticate.")

        self.drive = build('drive', 'v3', credentials=self.creds)
        print("[OK] Authentication successful!\n")

    def get_folder_info(self, folder_id):
        """Get information about a folder"""
        try:
            folder = self.drive.files().get(
                fileId=folder_id,
                fields='id, name, mimeType, owners, shared, capabilities',
                supportsAllDrives=True
            ).execute()

            print(f"Folder Info:")
            print(f"  Name: {folder.get('name')}")
            print(f"  ID: {folder.get('id')}")
            print(f"  Shared: {folder.get('shared')}")
            print(f"  Owners: {[o.get('emailAddress', o.get('displayName')) for o in folder.get('owners', [])]}")
            print()
            return folder
        except Exception as e:
            print(f"Error getting folder info: {e}\n")
            return None

    def list_folder_contents(self, folder_id):
        """List all items in a folder"""
        print(f"Scanning folder {folder_id}...")

        items = []
        page_token = None

        while True:
            response = self.drive.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields='nextPageToken, files(id, name, mimeType)',
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                corpora='allDrives'
            ).execute()

            items.extend(response.get('files', []))
            page_token = response.get('nextPageToken')

            if not page_token:
                break

        print(f"Found {len(items)} items\n")
        return items

    def find_november_folders(self, parent_folder_id):
        """Find all folders named 'November 2025'"""
        items = self.list_folder_contents(parent_folder_id)

        november_folders = [
            item for item in items
            if item['mimeType'] == 'application/vnd.google-apps.folder'
            and 'november' in item['name'].lower() and '2025' in item['name']
        ]

        print(f"Found {len(november_folders)} November 2025 folders:")
        for folder in november_folders:
            print(f"  - {folder['name']} (ID: {folder['id']})")
        print()

        return november_folders

    def find_zip_files(self, folder_id):
        """Find all zip files in a folder (including nested folders)"""
        print(f"Searching for zip files in folder...")

        all_items = []
        folders_to_scan = [folder_id]

        while folders_to_scan:
            current_folder = folders_to_scan.pop(0)
            items = self.list_folder_contents(current_folder)

            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    folders_to_scan.append(item['id'])
                elif item['name'].endswith('.zip'):
                    all_items.append(item)
                    print(f"  Found: {item['name']}")

        return all_items

    def create_folder(self, parent_id, folder_name):
        """Create a new folder in Google Drive"""
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

        print(f"[OK] Created folder: {folder['name']} (ID: {folder['id']})\n")
        return folder

    def move_file(self, file_id, file_name, new_parent_id, old_parent_id):
        """Move a file to a new parent folder"""
        print(f"Moving: {file_name}")

        self.drive.files().update(
            fileId=file_id,
            addParents=new_parent_id,
            removeParents=old_parent_id,
            fields='id, parents',
            supportsAllDrives=True
        ).execute()

        print(f"[OK] Moved successfully\n")

    def delete_folder(self, folder_id, folder_name):
        """Delete a folder"""
        print(f"Deleting empty folder: {folder_name}")

        self.drive.files().delete(
            fileId=folder_id,
            supportsAllDrives=True
        ).execute()

        print(f"[OK] Deleted\n")

    def consolidate_november_folders(self, parent_folder_id):
        """Main function to consolidate all November 2025 folders"""
        print("="*70)
        print("CONSOLIDATING NOVEMBER 2025 FOLDERS")
        print("="*70 + "\n")

        # First, check if we can access the parent folder
        folder_info = self.get_folder_info(parent_folder_id)
        if not folder_info:
            print("Cannot access the parent folder. Check permissions.")
            return

        # Find all November 2025 folders
        november_folders = self.find_november_folders(parent_folder_id)

        if not november_folders:
            print("No 'November 2025' folders found!")
            return

        if len(november_folders) == 1:
            print("Only one November 2025 folder exists. Nothing to consolidate!")
            return

        # Create or use the first November 2025 folder as the target
        target_folder = november_folders[0]
        print(f"Using '{target_folder['name']}' as the consolidated folder\n")

        # Collect all zip files from all November folders
        all_zip_files = []

        for folder in november_folders:
            print(f"\nScanning: {folder['name']}")
            print("-" * 70)
            zip_files = self.find_zip_files(folder['id'])

            for zip_file in zip_files:
                all_zip_files.append({
                    'file': zip_file,
                    'source_folder_id': folder['id'],
                    'source_folder_name': folder['name']
                })

            print(f"Found {len(zip_files)} zip files in this folder\n")

        print(f"\n{'='*70}")
        print(f"TOTAL ZIP FILES FOUND: {len(all_zip_files)}")
        print(f"{'='*70}\n")

        # Move all zip files to the target folder
        moved_count = 0
        for item in all_zip_files:
            zip_file = item['file']
            source_folder_id = item['source_folder_id']

            # Skip if already in target folder
            if source_folder_id == target_folder['id']:
                print(f"Skipping {zip_file['name']} (already in target folder)")
                continue

            try:
                self.move_file(
                    zip_file['id'],
                    zip_file['name'],
                    target_folder['id'],
                    source_folder_id
                )
                moved_count += 1
            except Exception as e:
                print(f"ERROR moving {zip_file['name']}: {e}\n")

        print(f"\n{'='*70}")
        print(f"MOVED {moved_count} ZIP FILES")
        print(f"{'='*70}\n")

        # Delete empty duplicate folders
        print("Cleaning up empty folders...\n")
        for folder in november_folders:
            # Skip the target folder
            if folder['id'] == target_folder['id']:
                continue

            # Check if folder is empty
            remaining_items = self.list_folder_contents(folder['id'])

            if len(remaining_items) == 0:
                try:
                    self.delete_folder(folder['id'], folder['name'])
                except Exception as e:
                    print(f"ERROR deleting {folder['name']}: {e}\n")
            else:
                print(f"Skipping {folder['name']} - still contains {len(remaining_items)} items\n")

        print("="*70)
        print("CONSOLIDATION COMPLETE!")
        print("="*70)
        print(f"\nAll zip files are now in: {target_folder['name']}")
        print(f"Total files consolidated: {len(all_zip_files)}")


def main():
    # The Google Drive folder ID from the URL
    PARENT_FOLDER_ID = '1pzot8MQ-m3u0f9-BWxpBO40QgLmeZhRP'

    organizer = DriveOrganizer()

    try:
        organizer.authenticate()
        organizer.consolidate_november_folders(PARENT_FOLDER_ID)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
