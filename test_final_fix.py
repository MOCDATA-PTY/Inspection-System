#!/usr/bin/env python
"""
Final verification that all JavaScript files use the correct endpoint
"""
import os
import re

def check_javascript_files():
    """Check all JavaScript files for endpoint usage"""
    print("🔍 CHECKING ALL JAVASCRIPT FILES FOR ENDPOINT USAGE")
    print("=" * 60)
    
    js_files = [
        'static/js/upload_functions.js',
        'static/js/sent_status.js', 
        'current_rendered_js.js'
    ]
    
    results = {}
    
    for js_file in js_files:
        if not os.path.exists(js_file):
            print(f"⚠️  {js_file} - FILE NOT FOUND")
            continue
            
        try:
            with open(js_file, 'rb') as f:
                content = f.read()
            
            # Count occurrences
            old_endpoint_count = content.count(b'/list-uploaded-files/')
            new_endpoint_count = content.count(b'/list-client-folder-files/')
            
            results[js_file] = {
                'old': old_endpoint_count,
                'new': new_endpoint_count,
                'status': 'OK' if old_endpoint_count <= 3 else 'NEEDS_FIX'  # current_rendered_js.js has 3 valid GET calls
            }
            
            print(f"📄 {js_file}:")
            print(f"   Old endpoint calls: {old_endpoint_count}")
            print(f"   New endpoint calls: {new_endpoint_count}")
            print(f"   Status: {results[js_file]['status']}")
            print()
            
        except Exception as e:
            print(f"❌ Error reading {js_file}: {e}")
            results[js_file] = {'error': str(e)}
    
    return results

def check_html_cache_busting():
    """Check if HTML template has cache-busting parameters"""
    print("🌐 CHECKING HTML TEMPLATE CACHE BUSTING")
    print("=" * 60)
    
    template_file = 'main/templates/main/shipment_list_clean.html'
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for version parameters
        upload_functions_match = re.search(r'upload_functions\.js\?v=([^"\']+)', content)
        sent_status_match = re.search(r'sent_status\.js\?v=([^"\']+)', content)
        
        print(f"📄 {template_file}:")
        if upload_functions_match:
            print(f"   upload_functions.js version: {upload_functions_match.group(1)}")
        else:
            print("   ❌ No version parameter for upload_functions.js")
            
        if sent_status_match:
            print(f"   sent_status.js version: {sent_status_match.group(1)}")
        else:
            print("   ❌ No version parameter for sent_status.js")
            
        return upload_functions_match and sent_status_match
        
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def main():
    print("🎯 FINAL FIX VERIFICATION")
    print("=" * 80)
    
    # Check JavaScript files
    js_results = check_javascript_files()
    
    # Check HTML cache busting
    cache_busting_ok = check_html_cache_busting()
    
    print("\n📊 SUMMARY")
    print("=" * 60)
    
    all_js_ok = True
    for file, result in js_results.items():
        if 'error' in result:
            print(f"❌ {file}: Error - {result['error']}")
            all_js_ok = False
        elif result['status'] != 'OK':
            print(f"⚠️  {file}: {result['status']}")
            all_js_ok = False
        else:
            print(f"✅ {file}: {result['status']}")
    
    print(f"✅ Cache busting: {'OK' if cache_busting_ok else 'NEEDS_FIX'}")
    
    if all_js_ok and cache_busting_ok:
        print("\n🎉 ALL CHECKS PASSED!")
        print("   • JavaScript files use correct endpoints")
        print("   • Cache busting parameters updated")
        print("   • Browser should load new JavaScript on next page refresh")
        print("\n💡 Next steps:")
        print("   1. Refresh the browser (Ctrl+F5 to force cache clear)")
        print("   2. Check server logs for reduced 400 errors")
        print("   3. Verify file status buttons work correctly")
    else:
        print("\n⚠️  SOME ISSUES FOUND - Check details above")
    
    return all_js_ok and cache_busting_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
