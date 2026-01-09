import os

# Change these values to test a specific client/date/folder
CLIENT_NAME = "Kwikspar Butterworth"
YEAR = "2025"
MONTH = "September"
BASE_PATH = r"D:\2025\Legal-System-2025-06-16-main\Legal-System-2025-06-16-main\media\inspection"

# Document folders to check
DOC_FOLDERS = ["Request For Invoice", "invoice", "lab results", "retest", "Compliance"]

def main():
    client_folder = os.path.join(BASE_PATH, YEAR, MONTH, CLIENT_NAME)
    print(f"Checking: {client_folder}")
    if not os.path.exists(client_folder):
        print(f"❌ Client folder does not exist: {client_folder}")
        return
    found_any = False
    for doc_folder in DOC_FOLDERS:
        folder_path = os.path.join(client_folder, doc_folder)
        if os.path.exists(folder_path):
            print(f"📁 Found folder: {folder_path}")
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    print(f"   ✅ File: {os.path.join(root, file)}")
                    found_any = True
        else:
            print(f"   ⚠️ Folder not found: {folder_path}")
    if not found_any:
        print("❌ No files found in any document folders.")

if __name__ == "__main__":
    main()
