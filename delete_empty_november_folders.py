"""
Delete all empty November folders except November 2025 FINAL
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

    PARENT_FOLDER_ID = '1pzot8MQ-m3u0f9-BWxpBO40QgLmeZhRP'

    print("="*70)
    print("DELETING EMPTY NOVEMBER FOLDERS")
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

    # Find all November folders
    november_folders = [f for f in folders if 'november' in f['name'].lower() and '2025' in f['name']]

    print(f"Found {len(november_folders)} November folders:\n")

    deleted_count = 0

    for folder in november_folders:
        # Skip "November 2025 FINAL"
        if folder['name'] == 'November 2025 FINAL':
            print(f"[KEEPING] {folder['name']}")
            continue

        # Check if folder is empty
        contents = drive.files().list(
            q=f"'{folder['id']}' in parents and trashed = false",
            fields='files(id)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora='allDrives',
            pageSize=10
        ).execute()

        item_count = len(contents.get('files', []))

        if item_count == 0:
            print(f"[DELETING] {folder['name']} (empty)")
            try:
                drive.files().delete(
                    fileId=folder['id'],
                    supportsAllDrives=True
                ).execute()
                deleted_count += 1
                print(f"  [OK] Deleted")
            except Exception as e:
                print(f"  [ERROR] {e}")
        else:
            print(f"[SKIPPING] {folder['name']} (contains {item_count} items)")

        print()

    print("="*70)
    print("COMPLETE")
    print("="*70)
    print(f"Deleted: {deleted_count} folders")
    print(f"Remaining: November 2025 FINAL (with all files)")


if __name__ == "__main__":
    main()
