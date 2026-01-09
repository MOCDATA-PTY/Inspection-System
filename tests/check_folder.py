"""
Check what files are in the source folder.
"""

import os
import pickle
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SOURCE_FOLDER_ID = '18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4'

def get_drive_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

service = get_drive_service()

# List all files in the source folder - no filters
print(f"Checking folder ID: {SOURCE_FOLDER_ID}\n")

# Try different queries
queries = [
    f"'{SOURCE_FOLDER_ID}' in parents and trashed=false",
    f"'{SOURCE_FOLDER_ID}' in parents",
    "trashed=false"  # List some files to verify connection works
]

for i, query in enumerate(queries):
    print(f"\n{'='*60}")
    print(f"Query {i+1}: {query}")
    print('='*60)

    try:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, parents)',
            pageSize=50
        ).execute()

        files = response.get('files', [])
        print(f"Found {len(files)} items\n")

        for file in files[:10]:  # Show first 10
            print(f"Name: {file['name']}")
            print(f"Type: {file.get('mimeType', 'N/A')}")
            print(f"Parents: {file.get('parents', 'N/A')}")
            print(f"ID: {file['id']}")
            print("-" * 40)

        if len(files) > 10:
            print(f"... and {len(files) - 10} more items")

    except Exception as e:
        print(f"Error: {e}")
