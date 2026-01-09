"""
Check what Shared Drives and folders the authenticated account can access
"""

import os
import pickle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def main():
    print("\n" + "="*80)
    print("  CHECKING GOOGLE DRIVE ACCESS")
    print("="*80 + "\n")

    # Authenticate
    creds = None
    token_path = 'token.pickle'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if creds and creds.expired and creds.refresh_token:
        print("Refreshing expired token...")
        creds.refresh(Request())
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    if not creds or not creds.valid:
        print("[ERROR] No valid credentials found!")
        return

    drive = build('drive', 'v3', credentials=creds)
    print("[OK] Authentication successful!\n")

    # Get user info
    try:
        about = drive.about().get(fields='user').execute()
        user = about.get('user', {})
        print(f"Authenticated as: {user.get('emailAddress', 'Unknown')}")
        print(f"Display Name: {user.get('displayName', 'Unknown')}\n")
    except Exception as e:
        print(f"Could not get user info: {e}\n")

    # List all Shared Drives the user has access to
    print("="*80)
    print("  ACCESSIBLE SHARED DRIVES")
    print("="*80 + "\n")

    try:
        shared_drives = []
        page_token = None

        while True:
            response = drive.drives().list(
                pageSize=100,
                pageToken=page_token
            ).execute()

            drives = response.get('drives', [])
            shared_drives.extend(drives)

            page_token = response.get('nextPageToken')
            if not page_token:
                break

        if shared_drives:
            print(f"Found {len(shared_drives)} Shared Drives:\n")
            for idx, shared_drive in enumerate(shared_drives, 1):
                print(f"{idx}. {shared_drive['name']}")
                print(f"   ID: {shared_drive['id']}\n")
        else:
            print("No Shared Drives found.\n")

    except Exception as e:
        print(f"Error listing Shared Drives: {e}\n")

    # Try to access the specific folder ID
    print("="*80)
    print("  TESTING SPECIFIC FOLDER ACCESS")
    print("="*80 + "\n")

    folder_id = '1pzot8MQ-m3u0f9-BWxpBO40QgLmeZhRP'
    print(f"Testing folder ID: {folder_id}\n")

    try:
        folder = drive.files().get(
            fileId=folder_id,
            fields='id, name, mimeType, driveId, owners, shared',
            supportsAllDrives=True
        ).execute()

        print("[SUCCESS] Folder is accessible!")
        print(f"  Name: {folder.get('name')}")
        print(f"  ID: {folder.get('id')}")
        print(f"  Type: {folder.get('mimeType')}")
        if folder.get('driveId'):
            print(f"  In Shared Drive: {folder.get('driveId')}")
        print()

    except Exception as e:
        print(f"[FAILED] Cannot access folder: {e}\n")
        print("Possible reasons:")
        print("  1. The folder ID is incorrect")
        print("  2. The authenticated account doesn't have permission")
        print("  3. The folder is in a Shared Drive you don't have access to")
        print("\nSolution:")
        print("  - Make sure you're authenticated with the correct Google account")
        print("  - Check that the account has access to the Shared Drive")
        print("  - Verify the folder URL/ID is correct\n")

    print("="*80 + "\n")


if __name__ == "__main__":
    main()
