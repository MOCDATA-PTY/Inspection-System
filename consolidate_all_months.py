"""
Consolidate all duplicate month folders starting from October 2025 onwards
"""

import os
import pickle
import time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class MonthConsolidator:
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
            print(f"    ERROR: {file_name}: {e}")
            return False

    def consolidate_month(self, parent_folder_id, month_name):
        """Consolidate all duplicate folders for a specific month"""
        print(f"\n{'='*70}")
        print(f"CONSOLIDATING: {month_name}")
        print(f"{'='*70}\n")

        # Find all folders for this month
        all_folders = self.list_folder_contents(parent_folder_id)
        month_folders = [
            f for f in all_folders
            if f['mimeType'] == 'application/vnd.google-apps.folder'
            and month_name.lower() in f['name'].lower()
        ]

        if not month_folders:
            print(f"No folders found for {month_name}")
            return

        print(f"Found {len(month_folders)} '{month_name}' folders:")
        for folder in month_folders:
            print(f"  - {folder['name']} (ID: {folder['id']})")

        if len(month_folders) == 1:
            print(f"\nOnly one folder exists - nothing to consolidate")
            return

        # Use the first folder as the target
        target_folder = month_folders[0]
        print(f"\nUsing '{target_folder['name']}' as the main folder\n")

        # Collect all zip files from all month folders
        all_files = []
        for folder in month_folders:
            if folder['id'] == target_folder['id']:
                continue

            zip_files = self.get_all_zip_files(folder['id'])
            print(f"Scanning: {folder['name']} - Found {len(zip_files)} files")

            for zf in zip_files:
                all_files.append({
                    'file_id': zf['id'],
                    'file_name': zf['name'],
                    'source_folder_id': folder['id']
                })

        if not all_files:
            print(f"\nNo files to move for {month_name}")
            return

        print(f"\nTotal files to move: {len(all_files)}")
        print("Moving files...")

        # Move files
        moved = 0
        for file_info in all_files:
            success = self.move_file(
                file_info['file_id'],
                file_info['file_name'],
                target_folder['id'],
                file_info['source_folder_id']
            )
            if success:
                moved += 1

            if moved % 50 == 0 and moved > 0:
                print(f"  Progress: {moved}/{len(all_files)} files moved")

            time.sleep(0.05)  # Small delay to avoid rate limiting

        print(f"\n[OK] Moved {moved}/{len(all_files)} files to '{target_folder['name']}'")

        # Move empty duplicate folders to trash
        print("\nCleaning up empty folders...")
        for folder in month_folders:
            if folder['id'] == target_folder['id']:
                continue

            # Check if empty
            contents = self.list_folder_contents(folder['id'])
            if len(contents) == 0:
                try:
                    self.drive.files().update(
                        fileId=folder['id'],
                        body={'trashed': True},
                        supportsAllDrives=True
                    ).execute()
                    print(f"  [TRASHED] {folder['name']}")
                except Exception as e:
                    print(f"  [ERROR] Could not trash {folder['name']}: {e}")

    def consolidate_all_months(self, parent_folder_id):
        """Consolidate all months from October 2025 onwards"""
        print("="*70)
        print("MULTI-MONTH CONSOLIDATION")
        print("="*70)

        # Months to consolidate (October 2025 onwards)
        months = [
            "October 2025",
            "November 2025",
            "December 2025"
        ]

        for month in months:
            self.consolidate_month(parent_folder_id, month)

        print(f"\n{'='*70}")
        print("ALL MONTHS CONSOLIDATED!")
        print(f"{'='*70}\n")


def main():
    PARENT_FOLDER_ID = '1pzot8MQ-m3u0f9-BWxpBO40QgLmeZhRP'

    consolidator = MonthConsolidator()

    try:
        consolidator.authenticate()
        consolidator.consolidate_all_months(PARENT_FOLDER_ID)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
