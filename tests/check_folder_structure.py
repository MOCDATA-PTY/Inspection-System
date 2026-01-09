"""
Better script to check the folder structure for Beckley Brothers
"""
import os

def show_tree(path, prefix="", max_depth=3, current_depth=0):
    """Show directory tree structure"""
    if current_depth >= max_depth:
        return

    try:
        items = sorted(os.listdir(path))
        for i, item in enumerate(items):
            item_path = os.path.join(path, item)
            is_last = (i == len(items) - 1)

            # Print the item
            connector = "+-- " if is_last else "|-- "
            if os.path.isdir(item_path):
                print(f"{prefix}{connector}[DIR] {item}/")
                # Recursively show subdirectories
                extension = "    " if is_last else "|   "
                show_tree(item_path, prefix + extension, max_depth, current_depth + 1)
            else:
                # Show file size
                size = os.path.getsize(item_path)
                size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                print(f"{prefix}{connector}[FILE] {item} ({size_str})")
    except PermissionError:
        print(f"{prefix}[Permission Denied]")
    except Exception as e:
        print(f"{prefix}[Error: {e}]")

print("=" * 80)
print("FOLDER STRUCTURE FOR BECKLEY BROTHERS")
print("=" * 80)

# Check both folders
folders_to_check = [
    "media/inspection/2025/November/beckley_brothers_poultry_farm",
    "media/inspection/2025/November/mobile_beckley_brothers_poultry_farm"
]

for folder in folders_to_check:
    print(f"\n[FOLDER] {folder}")
    if os.path.exists(folder):
        show_tree(folder)
    else:
        print("  [DOES NOT EXIST]")

print("\n" + "=" * 80)
