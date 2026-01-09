"""
Download a file from Google Drive by file ID
"""

import os
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def download_file(file_id, output_path):
    """Download a file from Google Drive"""

    # Authenticate
    creds = None
    if os.path.exists('token_drive.pickle'):
        with open('token_drive.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token_drive.pickle', 'wb') as token:
                pickle.dump(creds, token)
        else:
            print("No valid credentials found. Run authentication first.")
            return False

    # Build Drive service
    drive = build('drive', 'v3', credentials=creds)

    try:
        # Get file metadata
        file_metadata = drive.files().get(
            fileId=file_id,
            fields='name, mimeType, size',
            supportsAllDrives=True
        ).execute()

        file_name = file_metadata.get('name', 'downloaded_file')
        file_size = int(file_metadata.get('size', 0))

        print(f"Downloading: {file_name}")
        print(f"Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")

        # Download file
        request = drive.files().get_media(
            fileId=file_id,
            supportsAllDrives=True
        )

        # Write to output path
        if not output_path:
            output_path = file_name

        with open(output_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"Download progress: {int(status.progress() * 100)}%")

        print(f"\nDownloaded successfully to: {output_path}")
        return True

    except Exception as e:
        print(f"Error downloading file: {e}")
        return False


def download_from_url(drive_url, output_path=None):
    """Download file from a Google Drive URL"""

    # Extract file ID from URL
    if '/file/d/' in drive_url:
        file_id = drive_url.split('/file/d/')[1].split('/')[0]
    elif 'id=' in drive_url:
        file_id = drive_url.split('id=')[1].split('&')[0]
    else:
        print("Could not extract file ID from URL")
        return False

    print(f"File ID: {file_id}")
    return download_file(file_id, output_path)


if __name__ == "__main__":
    import sys

    # Import MediaIoBaseDownload here for the main execution
    from googleapiclient.http import MediaIoBaseDownload

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python download_file.py <file_id> [output_path]")
        print("  python download_file.py <drive_url> [output_path]")
        print()
        print("Examples:")
        print("  python download_file.py 1abc123def456ghi789")
        print("  python download_file.py 1abc123def456ghi789 output.zip")
        print("  python download_file.py https://drive.google.com/file/d/1abc123def456ghi789/view")
        sys.exit(1)

    file_id_or_url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Check if it's a URL or file ID
    if file_id_or_url.startswith('http'):
        download_from_url(file_id_or_url, output_path)
    else:
        download_file(file_id_or_url, output_path)
