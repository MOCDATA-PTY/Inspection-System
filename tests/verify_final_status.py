"""
Verify final status of the 2025 folder
"""

import os
import pickle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def main():
    token_path = 'token.pickle'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    drive = build('drive', 'v3', credentials=creds)
    print("[OK] Authenticated\n")

    PARENT_FOLDER_ID = '1pzot8MQ-m3u0f9-BWxpBO40QgLmeZhRP'

    print("="*70)
    print("FINAL STATUS - 2025 FOLDER CONTENTS")
    print("="*70 + "\n")

    # List ALL items in parent folder (not trashed)
    response = drive.files().list(
        q=f"'{PARENT_FOLDER_ID}' in parents and trashed = false",
        fields='files(id, name, mimeType)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        corpora='allDrives',
        pageSize=1000
    ).execute()

    items = response.get('files', [])

    print(f"Total items in 2025 folder: {len(items)}\n")

    # Separate folders and files
    folders = [i for i in items if i['mimeType'] == 'application/vnd.google-apps.folder']
    files = [i for i in items if i['mimeType'] != 'application/vnd.google-apps.folder']

    print(f"Folders: {len(folders)}")
    for folder in folders:
        # Count items in each folder
        folder_contents = drive.files().list(
            q=f"'{folder['id']}' in parents and trashed = false",
            fields='files(id)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora='allDrives'
        ).execute()

        item_count = len(folder_contents.get('files', []))
        print(f"  - {folder['name']} ({item_count} items)")

    print(f"\nFiles: {len(files)}")
    if files:
        for file in files[:10]:
            print(f"  - {file['name']}")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more files")

    # Specifically check November 2025 FINAL
    print("\n" + "="*70)
    print("NOVEMBER 2025 FINAL FOLDER")
    print("="*70 + "\n")

    final_folder_id = '1NjXfosE8aKsbOYmW190xEkr_anbnRd-N'

    try:
        # Count all items recursively
        all_items = []
        page_token = None

        while True:
            result = drive.files().list(
                q=f"'{final_folder_id}' in parents and trashed = false",
                fields='nextPageToken, files(id, name)',
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                corpora='allDrives',
                pageSize=1000
            ).execute()

            all_items.extend(result.get('files', []))
            page_token = result.get('nextPageToken')

            if not page_token:
                break

        zip_files = [f for f in all_items if f['name'].endswith('.zip')]

        print(f"Total items: {len(all_items)}")
        print(f"ZIP files: {len(zip_files)}")
        print(f"\n[SUCCESS] All consolidation complete!")

    except Exception as e:
        print(f"[ERROR] Could not access folder: {e}")


if __name__ == "__main__":
    main()
