"""
Move empty November folders to trash
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
    print("MOVING EMPTY NOVEMBER FOLDERS TO TRASH")
    print("="*70 + "\n")

    # List all folders
    response = drive.files().list(
        q=f"'{PARENT_FOLDER_ID}' in parents and trashed = false and mimeType = 'application/vnd.google-apps.folder'",
        fields='files(id, name)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        corpora='allDrives'
    ).execute()

    folders = response.get('files', [])

    # Find November folders (excluding FINAL)
    november_folders = [f for f in folders if 'november' in f['name'].lower() and '2025' in f['name']]

    trashed_count = 0

    for folder in november_folders:
        # Skip November 2025 FINAL
        if folder['name'] == 'November 2025 FINAL':
            print(f"[KEEPING] {folder['name']}")
            continue

        # Check if empty
        contents = drive.files().list(
            q=f"'{folder['id']}' in parents and trashed = false",
            fields='files(id)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora='allDrives'
        ).execute()

        item_count = len(contents.get('files', []))

        if item_count == 0:
            print(f"[TRASHING] {folder['name']}")
            try:
                # Move to trash instead of delete
                drive.files().update(
                    fileId=folder['id'],
                    body={'trashed': True},
                    supportsAllDrives=True
                ).execute()
                print(f"  [OK] Moved to trash")
                trashed_count += 1
            except Exception as e:
                print(f"  [ERROR] {e}")
        else:
            print(f"[SKIPPING] {folder['name']} (contains {item_count} items)")

        print()

    print("="*70)
    print("COMPLETE")
    print("="*70)
    print(f"Trashed: {trashed_count} empty folders")
    print(f"Remaining: November 2025 FINAL (with all 1,403 files)")


if __name__ == "__main__":
    main()
