#!/usr/bin/env python3
"""
Debug HTML content to find the issue
"""

import requests

def debug_html():
    """Debug the HTML content"""
    print("🔍 Debugging HTML content...")
    
    try:
        response = requests.get('http://127.0.0.1:8000/inspections/', timeout=30)
        
        if response.status_code == 200:
            content = response.text
            
            # Save the full HTML for inspection
            with open('debug_inspections_page.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Saved full HTML to debug_inspections_page.html")
            
            # Look for specific patterns
            print("\n🔍 Looking for specific patterns:")
            
            # Check for Django template errors
            if 'TemplateSyntaxError' in content:
                print("❌ TemplateSyntaxError found")
            if 'TemplateDoesNotExist' in content:
                print("❌ TemplateDoesNotExist found")
            if 'VariableDoesNotExist' in content:
                print("❌ VariableDoesNotExist found")
                
            # Check for authentication issues
            if 'login' in content.lower() and 'password' in content.lower():
                print("❌ Login page detected - authentication issue")
                
            # Check for any error messages
            if 'error' in content.lower():
                print("❌ Error content found")
                
            # Look for the main content area
            if 'shipmentsTable' in content:
                print("✅ shipmentsTable found")
            else:
                print("❌ shipmentsTable NOT found")
                
            # Check if we're getting a different page
            if '<title>' in content:
                import re
                title_match = re.search(r'<title>([^<]+)</title>', content)
                if title_match:
                    print(f"📄 Page title: {title_match.group(1)}")
                    
            # Check for any JavaScript errors
            if 'console.error' in content:
                print("❌ JavaScript errors found")
                
            # Look for the main container
            if 'container' in content:
                print("✅ Container found")
            else:
                print("❌ Container NOT found")
                
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    debug_html()
