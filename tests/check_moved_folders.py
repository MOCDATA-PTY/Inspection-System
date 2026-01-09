"""
Check what's in the 'November 2025 Moved files' folders
"""

import os
import pickle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def main():
    # Authenticate
    token_path = 'token.pickle'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    drive = build('drive', 'v3', credentials=creds)
    print("[OK] Authenticated\n")

    # Parent folder ID
    PARENT_FOLDER_ID = '1pzot8MQ-m3u0f9-BWxpBO40QgLmeZhRP'

    # List all folders
    response = drive.files().list(
        q=f"'{PARENT_FOLDER_ID}' in parents and trashed = false and mimeType = 'application/vnd.google-apps.folder'",
        fields='files(id, name)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        corpora='allDrives'
    ).execute()

    folders = response.get('files', [])

    # Find "November 2025 Moved files" folders
    moved_folders = [f for f in folders if 'moved files' in f['name'].lower()]

    print(f"Found {len(moved_folders)} 'Moved files' folders:\n")

    for folder in moved_folders:
        print(f"Folder: {folder['name']}")
        print(f"ID: {folder['id']}")
        print("-" * 70)

        # List contents
        contents = drive.files().list(
            q=f"'{folder['id']}' in parents and trashed = false",
            fields='files(id, name, mimeType)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora='allDrives',
            pageSize=1000
        ).execute()

        items = contents.get('files', [])

        if not items:
            print("  [EMPTY - Can be deleted]\n")
        else:
            print(f"  Contains {len(items)} items:")
            for item in items[:20]:  # Show first 20
                print(f"    - {item['name']}")
            if len(items) > 20:
                print(f"    ... and {len(items) - 20} more items")
            print()

    print("="*70)
    print("SUMMARY")
    print("="*70)
    for folder in moved_folders:
        contents = drive.files().list(
            q=f"'{folder['id']}' in parents and trashed = false",
            fields='files(id)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora='allDrives'
        ).execute()
        count = len(contents.get('files', []))
        status = "EMPTY - Safe to delete" if count == 0 else f"Contains {count} items"
        print(f"{folder['name']}: {status}")


if __name__ == "__main__":
    main()
