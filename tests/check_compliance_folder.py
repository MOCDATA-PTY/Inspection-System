"""
Check what folder the compliance pull function is using
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

    # The folder ID from the code
    CURRENT_FOLDER_ID = '18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4'

    # The 2025 folder where we consolidated November files
    NOVEMBER_PARENT_FOLDER = '1pzot8MQ-m3u0f9-BWxpBO40QgLmeZhRP'

    print("="*70)
    print("CHECKING COMPLIANCE FOLDER CONFIGURATION")
    print("="*70 + "\n")

    # Check current folder
    print("CURRENT folder in code:")
    print(f"  ID: {CURRENT_FOLDER_ID}\n")

    try:
        folder = drive.files().get(
            fileId=CURRENT_FOLDER_ID,
            fields='id, name, parents',
            supportsAllDrives=True
        ).execute()

        print(f"  Name: {folder.get('name')}")
        print(f"  Parents: {folder.get('parents', [])}\n")

        # Check what's in this folder
        contents = drive.files().list(
            q=f"'{CURRENT_FOLDER_ID}' in parents and trashed = false",
            fields='files(id, name, mimeType)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora='allDrives',
            pageSize=20
        ).execute()

        files = contents.get('files', [])
        print(f"  Contains {len(files)} items (showing first 20):")
        for file in files[:20]:
            print(f"    - {file['name']}")

    except Exception as e:
        print(f"  [ERROR] Cannot access folder: {e}\n")

    print("\n" + "="*70)
    print("November 2025 PARENT folder (where we consolidated):")
    print(f"  ID: {NOVEMBER_PARENT_FOLDER}\n")

    try:
        folder2 = drive.files().get(
            fileId=NOVEMBER_PARENT_FOLDER,
            fields='id, name',
            supportsAllDrives=True
        ).execute()

        print(f"  Name: {folder2.get('name')}\n")

        # List folders in this parent (should include "November 2025")
        contents2 = drive.files().list(
            q=f"'{NOVEMBER_PARENT_FOLDER}' in parents and trashed = false and mimeType = 'application/vnd.google-apps.folder'",
            fields='files(id, name)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora='allDrives'
        ).execute()

        folders = contents2.get('files', [])
        print(f"  Month folders inside:")
        for folder in folders:
            print(f"    - {folder['name']} (ID: {folder['id']})")

    except Exception as e:
        print(f"  [ERROR] Cannot access folder: {e}\n")

    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)
    print("\nThe compliance pull function should scan:")
    print(f"  1. The existing folder: {CURRENT_FOLDER_ID}")
    print(f"  2. AND the 2025 folder: {NOVEMBER_PARENT_FOLDER}")
    print(f"     - Specifically the 'November 2025' subfolder for November documents")


if __name__ == "__main__":
    main()
