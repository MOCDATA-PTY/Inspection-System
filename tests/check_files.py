"""
Check for Beckley Brothers Poultry Farm files in the inspection folder
"""
import os

media_root = "media/inspection"

print("=" * 80)
print("CHECKING FOR BECKLEY BROTHERS POULTRY FARM FILES")
print("=" * 80)

# Check if 2025/November exists
nov_2025_path = os.path.join(media_root, "2025", "November")
print(f"\n[1] Checking if November 2025 folder exists...")
print(f"    Path: {nov_2025_path}")
print(f"    Exists: {os.path.exists(nov_2025_path)}")

if os.path.exists(nov_2025_path):
    print(f"\n[2] Listing all folders in November 2025...")
    try:
        folders = os.listdir(nov_2025_path)
        print(f"    Found {len(folders)} folders:")
        for folder in sorted(folders):
            print(f"      - {folder}")

            # Check for Beckley
            if "beckley" in folder.lower():
                print(f"\n    [FOUND] Beckley Brothers folder: {folder}")
                beckley_path = os.path.join(nov_2025_path, folder)

                # List contents
                print(f"    Contents of {folder}:")
                for item in os.listdir(beckley_path):
                    item_path = os.path.join(beckley_path, item)
                    if os.path.isdir(item_path):
                        print(f"      [DIR] {item}/")
                        # List files in subdirectory
                        try:
                            subfiles = os.listdir(item_path)
                            for subfile in subfiles:
                                print(f"        - {subfile}")
                        except:
                            pass
                    else:
                        print(f"      [FILE] {item}")
    except Exception as e:
        print(f"    Error: {e}")
else:
    print(f"\n[2] Checking what exists in 2025 folder...")
    year_2025_path = os.path.join(media_root, "2025")
    if os.path.exists(year_2025_path):
        print(f"    2025 folder exists")
        months = os.listdir(year_2025_path)
        print(f"    Months found: {months}")
    else:
        print(f"    2025 folder does not exist")

    print(f"\n[3] Checking what exists in inspection folder...")
    if os.path.exists(media_root):
        years = os.listdir(media_root)
        print(f"    Years found: {years}")
    else:
        print(f"    Inspection folder does not exist: {media_root}")

print("\n" + "=" * 80)
