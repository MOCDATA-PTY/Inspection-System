"""
Test the view URL that should be generated
"""

from urllib.parse import quote

# The file path from the API response
file_path = "inspection/2025/November/avonlea_farm_cc/rfi/FSA-RFI-DU-251117.pdf"

# URL encode it
encoded_path = quote(file_path, safe='')

# Build the full URL
view_url = f"/inspections/download-file/?file={encoded_path}&source=local&action=view"

print("\n" + "="*100)
print("EXPECTED VIEW URL")
print("="*100 + "\n")

print(f"Original path: {file_path}")
print(f"Encoded path: {encoded_path}")
print(f"Full URL: {view_url}")

print("\n" + "="*100)
print("\nYou should see this URL in the browser console when clicking the eye icon.")
print("If you see /media/ instead, the JavaScript cache wasn't cleared.")
print("="*100 + "\n")
