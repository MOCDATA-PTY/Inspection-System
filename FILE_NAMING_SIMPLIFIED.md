# File Naming System - Simplified for Linux Compatibility

## Problem
Files were not being found after upload due to:
1. **Complex folder names** with spaces, special characters, and inconsistent casing
2. **Unicode encoding issues** (e.g., `\u002D` for dashes) in client names
3. **Case-sensitive Linux filesystems** not matching Windows-created folders
4. **Inconsistent naming** between upload and retrieval functions

## Solution
Implemented a **simple, Linux-friendly folder naming convention** that:
- Converts all names to **lowercase**
- Replaces **spaces and dashes** with underscores
- Removes **special characters** (parentheses, quotes, slashes, etc.)
- Uses **consistent naming** across all functions

## Examples

| Original Client Name              | Sanitized Folder Name          |
|-----------------------------------|--------------------------------|
| Meat Mania                        | meat_mania                     |
| Boxer Superstore - Kwamashu 2     | boxer_superstore_kwamashu_2    |
| Eggbert Eggs (Pty) Ltd - Arendnes | eggbert_eggs_pty_ltd_arendnes  |
| Pick 'n Pay - Burgersfort         | pick_n_pay_burgersfort         |
| SUPERSPAR - City Centre           | superspar_city_centre          |

## Folder Structure

```
media/
└── inspection/
    └── 2025/
        └── September/
            └── meat_mania/           ← Simple, lowercase, no spaces
                ├── rfi/
                ├── invoice/
                ├── lab/              ← Simplified from "lab results"
                ├── retest/
                └── compliance/       ← Lowercase (was "Compliance")
```

## Changes Made

### 1. Updated `create_folder_name()` Function
**Location:** `main/views/core_views.py` (lines ~2090-2104)

**Before:**
```python
def create_folder_name(name):
    return name.replace('/', ' ').strip()  # Kept spaces, special chars
```

**After:**
```python
def create_folder_name(name):
    """Create Linux-friendly folder name - simple and robust"""
    if not name:
        return "unknown_client"
    import re
    clean_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)
    clean_name = clean_name.replace(' ', '_').replace('-', '_')
    clean_name = re.sub(r'_+', '_', clean_name)
    clean_name = clean_name.strip('_').lower()
    return clean_name or "unknown_client"
```

### 2. Updated File Retrieval Functions
- `get_inspection_files_local()` - Now uses same sanitization
- `get_inspection_files()` - Main endpoint updated
- `check_compliance_documents_status_local()` - Updated

### 3. Simplified Folder Categories
**Before:**
```python
categories = {
    'rfi': 'rfi',
    'invoice': 'invoice',
    'lab': 'lab results',        # Space in name
    'retest': 'retest',
    'compliance': 'Compliance'    # Uppercase
}
```

**After:**
```python
categories = {
    'rfi': 'rfi',
    'invoice': 'invoice',
    'lab': 'lab',                 # No space
    'retest': 'retest',
    'compliance': 'compliance'    # Lowercase
}
```

### 4. Removed Complex Folder Matching
- Removed fuzzy/normalized folder name matching
- No need for "best match" logic
- Direct path checking only

## Testing

Run the test script to verify:
```bash
python test_simplified_file_system.py
```

## Migration Notes

**For existing files:**
- Old folders with spaces/special chars will not be found
- Either:
  1. **Rename existing folders** to match new convention, or
  2. **Re-upload files** using the web interface (recommended)

**Example rename commands (PowerShell):**
```powershell
# Example: Rename "Meat Mania" to "meat_mania"
Rename-Item "media\inspection\2025\September\Meat Mania" "meat_mania"

# Example: Rename nested folders
Rename-Item "media\inspection\2025\September\meat_mania\Compliance" "compliance"
```

## Benefits

✅ **Linux Compatible** - Works on any Unix/Linux system
✅ **No Encoding Issues** - ASCII-safe folder names
✅ **Case Insensitive** - All lowercase eliminates case problems
✅ **Simple to Debug** - Easy to read and understand
✅ **Consistent** - Same logic everywhere
✅ **Fast** - No complex matching or normalization

## How to Upload Files Now

1. Navigate to the inspections page
2. Click on any inspection row to expand it
3. Click "Upload RFI" or "Upload Invoice"
4. Select your file
5. File is saved to: `media/inspection/YYYY/Month/sanitized_client_name/rfi/`

## How to View Files

1. Click "View Files" button (should turn green/orange when files exist)
2. Files are fetched from the sanitized folder path
3. All file types (RFI, Invoice, Lab, Compliance) are displayed

## Troubleshooting

**Q: I uploaded a file but can't see it**
- Check the Django console/logs for the actual folder path created
- Verify the file exists in the expected location
- Check folder names are lowercase with underscores

**Q: Old files are not showing up**
- Old folders need to be renamed to match the new convention
- Or re-upload the files through the interface

**Q: Special characters in client names**
- Parentheses, quotes, slashes are removed
- Spaces and dashes become underscores
- Everything is lowercase

## Code Locations

- **Upload function:** `main/views/core_views.py:2090` (`create_folder_name()`)
- **File retrieval:** `main/views/core_views.py:6520` (`get_inspection_files_local()`)
- **Main endpoint:** `main/views/core_views.py:7125` (`get_inspection_files()`)
- **Compliance check:** `main/views/core_views.py:753` (`check_compliance_documents_status_local()`)

## Related Files
- `test_simplified_file_system.py` - Test script for naming convention
- `main/views/core_views.py` - All upload/retrieval logic

