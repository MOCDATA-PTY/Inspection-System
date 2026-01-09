#!/bin/bash
# Deploy Partial Matching Fix for Client Names with "/" characters
# This fixes the issue where client names like "t/a" create nested folder structures

echo "=================================="
echo "Deploying Partial Matching Fix"
echo "=================================="
echo ""

# Activate virtual environment
echo "[1/3] Activating virtual environment..."
cd /root/Inspection-System
source venv/bin/activate

# Backup current file
echo "[2/3] Creating backup..."
cp main/views/core_views.py main/views/core_views.py.backup.$(date +%Y%m%d_%H%M%S)

# Apply the fix using Python
echo "[3/3] Applying fix..."
python3 <<'PYTHON_SCRIPT'
import re

# Read the file
with open('main/views/core_views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Update list_client_folder_files() function (around line 2972-2984)
old_pattern_1 = r'''        # Check multiple variations: ORIGINAL NAME FIRST \(with spaces\), then sanitized variations
        # CRITICAL: Try original name first to handle folders created with spaces \(mobile/web upload inconsistency\)
        client_folder_variations = \[client_name, sanitized_client_name, sanitized_with_slash, sanitized_with_apostrophe\]

        # List files in document type folders \(checking multiple folder variations\)
        files_list = \{\}
        seen_files = set\(\)  # Track files to avoid duplicates

        # Check all folder variations for files
        for folder_variation in client_folder_variations:
            test_path = os\.path\.join\(parent_path, folder_variation\)
            if not os\.path\.exists\(test_path\):
                continue

            print\(f"\[DEBUG\] Checking folder: \{test_path\}"\)'''

new_pattern_1 = '''        # Check multiple variations: ORIGINAL NAME FIRST (with spaces), then sanitized variations
        # CRITICAL: Try original name first to handle folders created with spaces (mobile/web upload inconsistency)
        client_folder_variations = [client_name, sanitized_client_name, sanitized_with_slash, sanitized_with_apostrophe]

        # List files in document type folders (checking multiple folder variations)
        files_list = {}
        seen_files = set()  # Track files to avoid duplicates

        # Find all matching folders (exact and partial matches for nested "/" structures)
        matched_folders = []

        # First try exact matches
        for folder_variation in client_folder_variations:
            test_path = os.path.join(parent_path, folder_variation)
            if os.path.exists(test_path):
                matched_folders.append((test_path, folder_variation))
                print(f"[DEBUG] Found exact match: {folder_variation}")

        # If no exact match found, try partial matching (for client names with "/" that create nested dirs)
        if not matched_folders and os.path.exists(parent_path):
            try:
                print(f"[DEBUG] No exact match found, trying partial matching in: {parent_path}")
                # List all folders in parent_path
                available_folders = [f for f in os.listdir(parent_path) if os.path.isdir(os.path.join(parent_path, f))]
                print(f"[DEBUG] Available folders: {available_folders[:10]}")  # Show first 10

                # Try to find folders that partially match the client name
                for available_folder in available_folders:
                    # Check if this folder is a partial match (for names split by "/" like "t/a")
                    for folder_variation in client_folder_variations:
                        # Get the part before any "/" or special char
                        variation_prefix = folder_variation.split('/')[0].strip()

                        # Normalize for comparison (case insensitive, ignore underscores)
                        normalized_available = available_folder.lower().replace('_', ' ').strip()
                        normalized_prefix = variation_prefix.lower().replace('_', ' ').strip()

                        # Check if the available folder starts with the variation prefix
                        # This handles cases like "Marang Layers Farming Enterprises t/" matching "Marang Layers Farming Enterprises t/a..."
                        if normalized_available.startswith(normalized_prefix) and len(normalized_prefix) > 10:
                            potential_path = os.path.join(parent_path, available_folder)
                            matched_folders.append((potential_path, available_folder))
                            print(f"[DEBUG] Found partial match: {available_folder} for {folder_variation}")
                            break  # Found a match for this available folder, move to next
            except Exception as e:
                print(f"[DEBUG] Error during partial matching: {e}")

        print(f"[DEBUG] Total matched folders: {len(matched_folders)}")

        # Process all matched folders (both exact and partial matches)
        for test_path, folder_name in matched_folders:
            print(f"[DEBUG] Checking folder: {test_path}")'''

# Apply Fix 1
if old_pattern_1 in content:
    content = content.replace(old_pattern_1, new_pattern_1)
    print("✓ Applied Fix 1: list_client_folder_files() partial matching")
else:
    print("✗ Fix 1 pattern not found - may already be applied or file changed")

# Fix 2: Update get_inspection_files_local() function (around line 8941-8967)
# This is harder to match with regex, so we'll use a different approach
# Look for the specific section and replace it

old_pattern_2_start = "        # Try original client name first (as stored in database with spaces)\n        client_base_path = os.path.join(base_inspection_path, client_name)\n\n        # If original name doesn't exist, try converted name (with underscores/lowercase)\n        if not os.path.exists(client_base_path):\n            client_base_path = os.path.join(base_inspection_path, client_folder)"

new_pattern_2 = '''        # Try original client name first (as stored in database with spaces)
        client_base_path = os.path.join(base_inspection_path, client_name)

        # If original name doesn't exist, try converted name (with underscores/lowercase)
        if not os.path.exists(client_base_path):
            client_base_path = os.path.join(base_inspection_path, client_folder)

        # If still not found, try partial matching for client names with "/" that create nested dirs
        if not os.path.exists(client_base_path) and os.path.exists(base_inspection_path):
            try:
                print(f"[DEBUG get_inspection_files_local] No exact match, trying partial matching in: {base_inspection_path}")
                available_folders = [f for f in os.listdir(base_inspection_path) if os.path.isdir(os.path.join(base_inspection_path, f))]
                print(f"[DEBUG get_inspection_files_local] Available folders: {available_folders[:10]}")

                # Try both client_name and client_folder for matching
                client_variations = [client_name, client_folder]

                for available_folder in available_folders:
                    for variation in client_variations:
                        # Get the part before any "/" or special char
                        variation_prefix = variation.split('/')[0].strip()

                        # Normalize for comparison
                        normalized_available = available_folder.lower().replace('_', ' ').strip()
                        normalized_prefix = variation_prefix.lower().replace('_', ' ').strip()

                        # Check if the available folder starts with the variation prefix
                        if normalized_available.startswith(normalized_prefix) and len(normalized_prefix) > 10:
                            client_base_path = os.path.join(base_inspection_path, available_folder)
                            print(f"[DEBUG get_inspection_files_local] Found partial match: {available_folder} for {variation}")
                            break

                    if os.path.exists(client_base_path):
                        break  # Found a match, stop searching
            except Exception as e:
                print(f"[DEBUG get_inspection_files_local] Error during partial matching: {e}")'''

# Find the section and check if it needs updating
if old_pattern_2_start in content:
    # Find the complete old section
    import re
    # Match from the start pattern until the next "# Define file categories" or similar
    pattern = re.escape(old_pattern_2_start) + r'.*?(?=\n        # Define file categories)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_pattern_2 + content[match.end():]
        print("✓ Applied Fix 2: get_inspection_files_local() partial matching")
    else:
        print("✗ Fix 2: Could not find end of section")
else:
    print("✗ Fix 2 pattern not found - may already be applied or file changed")

# Write the updated content
with open('main/views/core_views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ File updated successfully!")
PYTHON_SCRIPT

# Restart the service
echo ""
echo "Restarting service..."
sudo systemctl restart inspection-system

echo ""
echo "=================================="
echo "Deployment Complete!"
echo "=================================="
echo ""
echo "Changes applied:"
echo "  1. Added partial client folder matching in list_client_folder_files()"
echo "  2. Added partial client folder matching in get_inspection_files_local()"
echo ""
echo "This should now find files for client names with '/' characters"
echo "like 'Marang Layers Farming Enterprises t/a Maranga Eggs'"
echo ""
echo "Test by searching for: Marang Layers Farming Enterprises t/a Maranga Eggs"
echo "Date: 2025-10-01"
