import os
import sys
import json
import datetime
from pathlib import Path
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('file_visibility_test.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_django_env():
    """Set up Django environment for testing"""
    try:
        import django
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = current_dir  # The manage.py is in the same directory
        sys.path.append(project_dir)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
        django.setup()
        logger.info("✅ Django environment setup successful")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to setup Django environment: {e}")
        logger.error("Current directory structure:")
        for root, dirs, files in os.walk(current_dir):
            level = root.replace(current_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            logger.error(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                logger.error(f"{subindent}{f}")
        return False

def inspect_folder_structure(base_path, indent=""):
    """Recursively inspect and log the folder structure"""
    try:
        if not os.path.exists(base_path):
            logger.error(f"❌ Path does not exist: {base_path}")
            return

        logger.info(f"{indent}📂 Inspecting: {base_path}")
        items = os.listdir(base_path)
        
        for item in items:
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path):
                logger.info(f"{indent}  📁 DIR: {item}")
                # Check directory permissions
                try:
                    os.listdir(item_path)
                    logger.info(f"{indent}    ✅ Directory is readable")
                except PermissionError:
                    logger.error(f"{indent}    ❌ Permission denied: {item_path}")
                inspect_folder_structure(item_path, indent + "  ")
            else:
                # Get detailed file info
                try:
                    size = os.path.getsize(item_path)
                    modified = datetime.datetime.fromtimestamp(os.path.getmtime(item_path))
                    logger.info(f"{indent}  📄 FILE: {item} (Size: {size:,} bytes, Modified: {modified})")
                except Exception as e:
                    logger.error(f"{indent}  ❌ Error getting file details for {item}: {e}")
    except Exception as e:
        logger.error(f"❌ Error inspecting folder structure at {base_path}: {e}")

def test_file_discovery(client_name, inspection_date):
    """Test file discovery logic"""
    logger.info("\n🔍 TESTING FILE DISCOVERY")
    logger.info(f"Client: {client_name}")
    logger.info(f"Date: {inspection_date}")

    try:
        # Try to get settings from Django, fallback to local path if Django isn't set up
        try:
            from django.conf import settings
            MEDIA_ROOT = settings.MEDIA_ROOT
        except:
            MEDIA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')
            logger.warning(f"⚠️ Using fallback MEDIA_ROOT: {MEDIA_ROOT}")
        
        try:
            from main.views.core_views import get_inspection_files_local
            USING_DJANGO = True
        except:
            USING_DJANGO = False
            logger.warning("⚠️ Could not import Django views, will test file system only")
        
        # 1. Test direct path construction
        date_obj = datetime.datetime.strptime(inspection_date, '%Y-%m-%d')
        year_folder = date_obj.strftime('%Y')
        month_folder = date_obj.strftime('%B')
        
        # Build all possible paths
        paths_to_check = []
        base_path = os.path.join(settings.MEDIA_ROOT, 'inspection', year_folder, month_folder)
        
        # Test different client name variations
        client_variations = [
            client_name,
            client_name.replace(' ', '_'),
            client_name.replace(' ', '-'),
            client_name.replace(' - ', '_'),
            client_name.replace(' - ', ' '),
            client_name.replace('_', ' '),
            client_name.replace('_', '-')
        ]
        
        for client_var in client_variations:
            full_path = os.path.join(base_path, client_var)
            paths_to_check.append(full_path)
            logger.info(f"\n🔍 Checking path variation: {full_path}")
            
            if os.path.exists(full_path):
                logger.info("✅ Path exists!")
                # Deep inspect this path
                inspect_folder_structure(full_path)
                
                # Check specific document folders
                doc_folders = ['Request For Invoice', 'invoice', 'lab results', 'retest', 'Compliance']
                for folder in doc_folders:
                    folder_path = os.path.join(full_path, folder)
                    if os.path.exists(folder_path):
                        logger.info(f"\n📁 Found {folder} folder:")
                        inspect_folder_structure(folder_path)
                
                # Check for Inspection-XXXX folders
                inspection_folders = [d for d in os.listdir(full_path) if d.startswith('Inspection-')]
                for insp_folder in inspection_folders:
                    insp_path = os.path.join(full_path, insp_folder)
                    logger.info(f"\n🔍 Inspecting {insp_folder}:")
                    inspect_folder_structure(insp_path)
            else:
                logger.warning(f"❌ Path does not exist: {full_path}")

        # 2. Test get_inspection_files_local if available
        if USING_DJANGO:
            logger.info("\n🔧 Testing get_inspection_files_local function:")
            try:
                files = get_inspection_files_local(client_name, inspection_date, force_refresh=True)
                logger.info("\n📋 Files returned by get_inspection_files_local:")
                logger.info(json.dumps(files, indent=2))
                
                if not files:
                    logger.warning("⚠️ No files returned from get_inspection_files_local")
            except Exception as e:
                logger.error(f"❌ Error in get_inspection_files_local: {e}", exc_info=True)
        else:
            logger.info("⏩ Skipping get_inspection_files_local test (Django not available)")
            
            # Analyze results
            total_files = sum(len(files.get(cat, [])) for cat in files)
            logger.info(f"\n📊 Results Summary:")
            logger.info(f"Total files found: {total_files}")
            for category, file_list in files.items():
                logger.info(f"{category}: {len(file_list)} files")
                for file in file_list:
                    logger.info(f"  - {file['path']} ({file['size']:,} bytes)")
        except Exception as e:
            logger.error(f"❌ Error in get_inspection_files_local: {e}", exc_info=True)

        # 3. Test file permissions and readability
        logger.info("\n🔒 Testing file permissions and readability")
        for path in paths_to_check:
            if os.path.exists(path):
                try:
                    # Test directory listing
                    items = os.listdir(path)
                    logger.info(f"✅ Can list directory: {path}")
                    
                    # Test file reading for each file
                    for item in items:
                        item_path = os.path.join(path, item)
                        if os.path.isfile(item_path):
                            try:
                                with open(item_path, 'rb') as f:
                                    # Try to read first few bytes
                                    f.read(1024)
                                logger.info(f"✅ Can read file: {item}")
                            except Exception as e:
                                logger.error(f"❌ Cannot read file {item}: {e}")
                except Exception as e:
                    logger.error(f"❌ Permission error on {path}: {e}")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)

def test_file_display(client_name, inspection_date):
    """Test file display logic"""
    logger.info("\n🖥️ TESTING FILE DISPLAY")
    
    try:
        from django.test import RequestFactory
        from main.views.core_views import list_uploaded_files
        
        # Create a test request
        factory = RequestFactory()
        request = factory.get('/list-uploaded-files/', {
            'client_name': client_name,
            'inspection_date': inspection_date
        })
        
        # Test the view
        logger.info("🔍 Testing list_uploaded_files view")
        response = list_uploaded_files(request)
        
        # Analyze response
        if response:
            content = json.loads(response.content)
            logger.info("\n📋 Response content:")
            logger.info(json.dumps(content, indent=2))
            
            if isinstance(content, dict):
                if content.get('success') is True:
                    files = content.get('files', {})
                    logger.info(f"\n📊 Files in response:")
                    for category, file_list in files.items():
                        logger.info(f"{category}: {len(file_list)} files")
                        for file in file_list:
                            logger.info(f"  - {file['name']} ({file['size']:,} bytes)")
                else:
                    logger.error(f"❌ Response indicates failure: {content.get('error', 'No error message')}")
        else:
            logger.error("❌ No response from view")
            
    except Exception as e:
        logger.error(f"❌ Display test failed: {e}", exc_info=True)

def main():
    """Main test execution"""
    logger.info("🚀 Starting comprehensive file visibility test")
    
    # Initialize Django
    if not setup_django_env():
        return
    
    # Test configuration
    test_cases = [
        {
            'client_name': 'Northcrest Superspar',
            'inspection_date': '2025-09-22'
        },
        # Add more test cases if needed
    ]
    
    # Run tests for each case
    for test_case in test_cases:
        logger.info(f"\n==== Testing {test_case['client_name']} on {test_case['inspection_date']} ====")
        
        # Run discovery tests
        test_file_discovery(test_case['client_name'], test_case['inspection_date'])
        
        # Run display tests
        test_file_display(test_case['client_name'], test_case['inspection_date'])
        
    logger.info("\n✨ Test completion")

if __name__ == '__main__':
    main()
