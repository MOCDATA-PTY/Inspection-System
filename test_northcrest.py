import os
import sys
import json
import datetime
import logging
from pathlib import Path

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('file_test.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_folder_access(path):
    """Test access to a folder and its contents"""
    logger.info(f"\nTesting access to: {path}")
    try:
        if os.path.exists(path):
            logger.info(f"✓ Path exists")
            try:
                items = os.listdir(path)
                logger.info(f"✓ Can list directory contents ({len(items)} items)")
                return items
            except PermissionError:
                logger.error(f"✗ Permission denied when trying to list contents")
                return None
        else:
            logger.error(f"✗ Path does not exist")
            parent = os.path.dirname(path)
            if os.path.exists(parent):
                logger.info(f"Parent exists: {parent}")
                parent_items = os.listdir(parent)
                logger.info(f"Parent contents: {parent_items}")
            return None
    except Exception as e:
        logger.error(f"Error testing folder access: {e}")
        return None

def scan_folder_contents(path, indent=""):
    """Recursively scan folder contents and log details"""
    if not os.path.exists(path):
        logger.error(f"{indent}Path does not exist: {path}")
        return
    
    logger.info(f"{indent}Contents of: {path}")
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                logger.info(f"{indent}[DIR] {item}")
                scan_folder_contents(item_path, indent + "  ")
            else:
                try:
                    size = os.path.getsize(item_path)
                    modified = datetime.datetime.fromtimestamp(os.path.getmtime(item_path))
                    readable = os.access(item_path, os.R_OK)
                    logger.info(f"{indent}[FILE] {item}")
                    logger.info(f"{indent}      Size: {size:,} bytes")
                    logger.info(f"{indent}      Modified: {modified}")
                    logger.info(f"{indent}      Readable: {readable}")
                except Exception as e:
                    logger.error(f"{indent}Error getting file details for {item}: {e}")
    except Exception as e:
        logger.error(f"Error scanning folder {path}: {e}")

def check_northcrest_files():
    """Check specifically for Northcrest Superspar files"""
    client_name = "Northcrest Superspar"
    date_str = "2025-09-22"
    
    # Calculate folder paths
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    year_folder = date_obj.strftime('%Y')
    month_folder = date_obj.strftime('%B')
    
    # Get script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try multiple possible media roots
    possible_roots = [
        os.path.join(script_dir, 'media'),
        os.path.join(script_dir, '..', 'media'),
        os.path.join(script_dir, 'inspection_system', 'media'),
        'D:/2025/Legal-System-2025-06-16-main/Legal-System-2025-06-16-main/media'
    ]
    
    # Test each possible media root
    for media_root in possible_roots:
        logger.info(f"\nChecking media root: {media_root}")
        base_path = os.path.join(media_root, 'inspection', year_folder, month_folder, client_name)
        
        if os.path.exists(media_root):
            logger.info(f"✓ Media root exists")
            
            # Check the full path
            logger.info(f"\nChecking base path: {base_path}")
            if os.path.exists(base_path):
                logger.info(f"✓ Client folder exists")
                
                # List and check each folder
                scan_folder_contents(base_path)
                
                # Specifically check Inspection folders
                inspection_folders = [d for d in os.listdir(base_path) if d.startswith('Inspection-')]
                for folder in inspection_folders:
                    insp_path = os.path.join(base_path, folder)
                    logger.info(f"\nChecking inspection folder: {folder}")
                    scan_folder_contents(insp_path)
                    
                    # Check for compliance files
                    compliance_path = os.path.join(insp_path, 'Compliance')
                    if os.path.exists(compliance_path):
                        logger.info(f"\nFound Compliance folder in {folder}")
                        scan_folder_contents(compliance_path)
            else:
                logger.error(f"✗ Client folder not found")
                # Check parent folders
                current = base_path
                while current != media_root:
                    parent = os.path.dirname(current)
                    if os.path.exists(parent):
                        logger.info(f"Parent exists: {parent}")
                        try:
                            items = os.listdir(parent)
                            logger.info(f"Contents: {items}")
                        except Exception as e:
                            logger.error(f"Error listing parent contents: {e}")
                        break
                    current = parent
        else:
            logger.error(f"✗ Media root not found: {media_root}")

def main():
    """Main test execution"""
    logger.info("Starting Northcrest Superspar file test\n")
    check_northcrest_files()
    logger.info("\nTest completed")

if __name__ == '__main__':
    main()
