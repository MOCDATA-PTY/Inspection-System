#!/usr/bin/env python
"""
Test script to verify list_client_folder_files import and functionality
"""
import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# Setup Django
django.setup()

def test_import():
    """Test if list_client_folder_files can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from main.views.core_views import list_client_folder_files
        print("✅ Successfully imported list_client_folder_files from core_views")
    except ImportError as e:
        print(f"❌ Failed to import from core_views: {e}")
        return False
    
    try:
        from main.views import list_client_folder_files
        print("✅ Successfully imported list_client_folder_files from main.views")
    except ImportError as e:
        print(f"❌ Failed to import from main.views: {e}")
        return False
    
    return True

def test_function_exists():
    """Test if the function actually exists in the module"""
    print("\n🔍 Testing function existence...")
    
    try:
        import main.views.core_views as core_views
        if hasattr(core_views, 'list_client_folder_files'):
            print("✅ list_client_folder_files exists in core_views module")
            func = getattr(core_views, 'list_client_folder_files')
            print(f"✅ Function type: {type(func)}")
            print(f"✅ Function docstring: {func.__doc__}")
        else:
            print("❌ list_client_folder_files NOT found in core_views module")
            print("Available functions:")
            for name in dir(core_views):
                if not name.startswith('_') and callable(getattr(core_views, name)):
                    print(f"  - {name}")
            return False
    except Exception as e:
        print(f"❌ Error checking core_views: {e}")
        return False
    
    return True

def test_views_init():
    """Test the main.views.__init__.py imports"""
    print("\n📦 Testing main.views module...")
    
    try:
        import main.views as views
        if hasattr(views, 'list_client_folder_files'):
            print("✅ list_client_folder_files exists in main.views")
        else:
            print("❌ list_client_folder_files NOT found in main.views")
            print("Available attributes in main.views:")
            for name in dir(views):
                if not name.startswith('_'):
                    print(f"  - {name}")
            return False
    except Exception as e:
        print(f"❌ Error checking main.views: {e}")
        return False
    
    return True

def test_url_resolution():
    """Test URL resolution"""
    print("\n🌐 Testing URL resolution...")
    
    try:
        from django.urls import reverse
        url = reverse('list_client_folder_files')
        print(f"✅ URL resolved: {url}")
    except Exception as e:
        print(f"❌ URL resolution failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("🔧 DJANGO IMPORT TEST SCRIPT")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_import),
        ("Function Existence Test", test_function_exists),
        ("Views Init Test", test_views_init),
        ("URL Resolution Test", test_url_resolution)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 All tests passed! The import should work now.")
    else:
        print("\n💥 Some tests failed. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)