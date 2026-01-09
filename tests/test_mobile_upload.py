"""
Test script to simulate mobile file upload and check where files are stored
"""
import os
import requests
from io import BytesIO

# Django server URL
BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = "/upload-document/"

# Test credentials
USERNAME = "developer"
PASSWORD = "Ethan4269875321"

def test_mobile_upload():
    """Simulate a mobile file upload and check where it's stored"""

    print("=" * 80)
    print("TESTING MOBILE FILE UPLOAD")
    print("=" * 80)

    # Create a session
    session = requests.Session()

    # Step 1: Login
    print("\n[1] Logging in...")
    login_page = session.get(f"{BASE_URL}/login/")
    csrf_token = session.cookies.get('csrftoken')

    if not csrf_token:
        print("    [ERROR] Failed to get CSRF token")
        return

    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token
    }
    login_response = session.post(
        f"{BASE_URL}/login/",
        data=login_data,
        headers={'Referer': f"{BASE_URL}/login/"}
    )

    if 'sessionid' in session.cookies:
        print("    [OK] Login successful")
    else:
        print("    [ERROR] Login failed")
        return

    # Step 2: Create a dummy PDF file
    print("\n[2] Creating dummy PDF file...")
    # Simple PDF header (minimal valid PDF)
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Mobile Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
410
%%EOF
"""

    print("    [OK] Created dummy PDF (410 bytes)")

    # Step 3: Simulate MOBILE upload with group_id for Beckley Brothers
    print("\n[3] Simulating MOBILE upload...")

    # This is the group_id format used by mobile cards
    # Format: ClientName_YYYYMMDD (from fallback_group_id in template)
    group_id = "Beckley_Brothers_Poultry_Farm_20251107"

    print(f"    Group ID: {group_id}")
    print(f"    Document Type: RFI")
    print(f"    Upload Source: MOBILE (simulated)")

    # Update CSRF token
    csrf_token = session.cookies.get('csrftoken')

    # Create form data (exactly as mobile upload would send it)
    files = {
        'file': ('mobile-test-rfi.pdf', BytesIO(pdf_content), 'application/pdf')
    }
    data = {
        'group_id': group_id,
        'document_type': 'rfi',
        'csrfmiddlewaretoken': csrf_token
    }

    print(f"\n[4] Uploading file...")
    print(f"    Endpoint: {UPLOAD_ENDPOINT}")
    print(f"    Form data:")
    print(f"      - group_id: {group_id}")
    print(f"      - document_type: rfi")
    print(f"      - file: mobile-test-rfi.pdf")

    response = session.post(
        f"{BASE_URL}{UPLOAD_ENDPOINT}",
        files=files,
        data=data,
        headers={'X-CSRFToken': csrf_token}
    )

    print(f"\n[5] Upload response (status: {response.status_code})")

    if response.status_code == 200:
        try:
            result = response.json()
            print(f"    Success: {result.get('success', False)}")
            print(f"    Message: {result.get('message', 'N/A')}")
            if 'error' in result:
                print(f"    Error: {result['error']}")
        except:
            print(f"    Raw response: {response.text[:500]}")
    else:
        print(f"    [ERROR] Upload failed")
        print(f"    Response: {response.text[:500]}")

    # Step 4: Check where the file was stored
    print("\n" + "=" * 80)
    print("CHECKING FILE LOCATION")
    print("=" * 80)

    media_root = "media/inspection/2025/November"

    if not os.path.exists(media_root):
        print(f"\n[ERROR] Media root doesn't exist: {media_root}")
        return

    print(f"\n[6] Scanning {media_root}...")

    folders_found = []
    for folder_name in os.listdir(media_root):
        folder_path = os.path.join(media_root, folder_name)
        if os.path.isdir(folder_path):
            folders_found.append(folder_name)
            print(f"\n  [FOLDER] Found folder: {folder_name}")

            # Check for RFI subfolder
            rfi_path = os.path.join(folder_path, 'rfi')
            if os.path.exists(rfi_path):
                print(f"    [OK] Has RFI folder")
                files = os.listdir(rfi_path)
                if files:
                    print(f"    Files in RFI folder:")
                    for file in files:
                        file_path = os.path.join(rfi_path, file)
                        size = os.path.getsize(file_path)
                        print(f"      - {file} ({size} bytes)")
                else:
                    print(f"    (RFI folder is empty)")
            else:
                print(f"    [ERROR] No RFI folder")

    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print("=" * 80)
    print(f"Total client folders found: {len(folders_found)}")
    for folder in folders_found:
        print(f"  - {folder}")

    # Check for both regular and mobile-prefixed folders
    has_regular = any('beckley' in f.lower() and not f.startswith('mobile_') for f in folders_found)
    has_mobile = any(f.startswith('mobile_') and 'beckley' in f.lower() for f in folders_found)

    print(f"\nFolder analysis:")
    print(f"  Regular folder (beckley_brothers_poultry_farm): {'[OK] EXISTS' if has_regular else '[ERROR] NOT FOUND'}")
    print(f"  Mobile folder (mobile_beckley_brothers_poultry_farm): {'[WARNING] EXISTS (PROBLEM!)' if has_mobile else '[OK] NOT FOUND (GOOD!)'}")

    if has_mobile:
        print(f"\n[WARNING] Mobile uploads are creating separate 'mobile_' prefixed folders!")
        print(f"   This is the bug we need to fix.")
    elif has_regular:
        print(f"\n[SUCCESS] Mobile upload used the same folder as desktop!")
        print(f"   Both mobile and desktop uploads go to the same location.")

    print(f"\n{'=' * 80}")

if __name__ == "__main__":
    test_mobile_upload()
