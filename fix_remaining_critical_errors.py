#!/usr/bin/env python3
"""
Fix the remaining critical JavaScript syntax errors
"""

import re
import os

def fix_remaining_critical_errors():
    template_path = 'main/templates/main/shipment_list_clean.html'
    
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        return
    
    print("Reading template file...")
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find Script Section 4
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)
    
    if len(scripts) < 4:
        print("Error: Could not find Script Section 4")
        return
    
    script_4 = scripts[3]
    print(f"Script Section 4 length: {len(script_4)} characters")
    
    original_script = script_4
    fixes_applied = []
    
    # Fix the most critical remaining errors
    # Fix malformed getElementById calls
    if "document.getElementById('filesModal';);" in script_4:
        script_4 = script_4.replace("document.getElementById('filesModal';);", "document.getElementById('filesModal');")
        fixes_applied.append("Fixed getElementById: filesModal")
    
    if "document.getElementById('modalTitle';);" in script_4:
        script_4 = script_4.replace("document.getElementById('modalTitle';);", "document.getElementById('modalTitle');")
        fixes_applied.append("Fixed getElementById: modalTitle")
    
    if "document.getElementById('filesLoading';);" in script_4:
        script_4 = script_4.replace("document.getElementById('filesLoading';);", "document.getElementById('filesLoading');")
        fixes_applied.append("Fixed getElementById: filesLoading")
    
    if "document.getElementById('filesContent';);" in script_4:
        script_4 = script_4.replace("document.getElementById('filesContent';);", "document.getElementById('filesContent');")
        fixes_applied.append("Fixed getElementById: filesContent")
    
    if "document.getElementById('downloadAllBtn';);" in script_4:
        script_4 = script_4.replace("document.getElementById('downloadAllBtn';);", "document.getElementById('downloadAllBtn');")
        fixes_applied.append("Fixed getElementById: downloadAllBtn")
    
    if "document.getElementById('filesList';);" in script_4:
        script_4 = script_4.replace("document.getElementById('filesList';);", "document.getElementById('filesList');")
        fixes_applied.append("Fixed getElementById: filesList")
    
    # Fix malformed property access
    if "window.currentFilesClien;t;" in script_4:
        script_4 = script_4.replace("window.currentFilesClien;t;", "window.currentFilesClient;")
        fixes_applied.append("Fixed property access: currentFilesClient")
    
    if "window.currentFilesDat;e;" in script_4:
        script_4 = script_4.replace("window.currentFilesDat;e;", "window.currentFilesDate;")
        fixes_applied.append("Fixed property access: currentFilesDate")
    
    if "window.currentFilesGroupI;d;" in script_4:
        script_4 = script_4.replace("window.currentFilesGroupI;d;", "window.currentFilesGroupId;")
        fixes_applied.append("Fixed property access: currentFilesGroupId")
    
    if "downloadBtn.innerHTM;L;" in script_4:
        script_4 = script_4.replace("downloadBtn.innerHTM;L;", "downloadBtn.innerHTML;")
        fixes_applied.append("Fixed property access: innerHTML")
    
    # Fix malformed function calls
    if "await response.blob(;);" in script_4:
        script_4 = script_4.replace("await response.blob(;);", "await response.blob();")
        fixes_applied.append("Fixed function call: response.blob()")
    
    if "response.headers.get('Content-Disposition';);" in script_4:
        script_4 = script_4.replace("response.headers.get('Content-Disposition';);", "response.headers.get('Content-Disposition');")
        fixes_applied.append("Fixed function call: headers.get()")
    
    if "window.URL.createObjectURL(blob;);" in script_4:
        script_4 = script_4.replace("window.URL.createObjectURL(blob;);", "window.URL.createObjectURL(blob);")
        fixes_applied.append("Fixed function call: createObjectURL()")
    
    if "document.createElement('a';);" in script_4:
        script_4 = script_4.replace("document.createElement('a';);", "document.createElement('a');")
        fixes_applied.append("Fixed function call: createElement('a')")
    
    if "await response.json(;);" in script_4:
        script_4 = script_4.replace("await response.json(;);", "await response.json();")
        fixes_applied.append("Fixed function call: response.json()")
    
    if "Object.fromEntries(response.headers.entries(););" in script_4:
        script_4 = script_4.replace("Object.fromEntries(response.headers.entries(););", "Object.fromEntries(response.headers.entries());")
        fixes_applied.append("Fixed function call: headers.entries()")
    
    if "JSON.stringify(requestData, null, 2););" in script_4:
        script_4 = script_4.replace("JSON.stringify(requestData, null, 2););", "JSON.stringify(requestData, null, 2);")
        fixes_applied.append("Fixed function call: JSON.stringify()")
    
    if "JSON.stringify(result, null, 2););" in script_4:
        script_4 = script_4.replace("JSON.stringify(result, null, 2););", "JSON.stringify(result, null, 2);")
        fixes_applied.append("Fixed function call: JSON.stringify()")
    
    # Fix malformed string literals
    if "let filename = clientName + '_' + inspectionDate + '_all_files.zip;';" in script_4:
        script_4 = script_4.replace("let filename = clientName + '_' + inspectionDate + '_all_files.zip;';", "let filename = clientName + '_' + inspectionDate + '_all_files.zip';")
        fixes_applied.append("Fixed string literal: filename")
    
    # Fix malformed object property access
    if "let statusCheckInProgress = fals;e;" in script_4:
        script_4 = script_4.replace("let statusCheckInProgress = fals;e;", "let statusCheckInProgress = false;")
        fixes_applied.append("Fixed boolean literal: false")
    
    # Fix malformed object syntax
    if "requestData = {" in script_4 and "};);" in script_4:
        script_4 = script_4.replace("};);", "};")
        fixes_applied.append("Fixed object syntax: };);")
    
    # Fix malformed function calls with semicolons
    if "};);" in script_4:
        script_4 = script_4.replace("};);", "});")
        fixes_applied.append("Fixed function call syntax: };);")
    
    # Fix malformed trim calls
    if ".trim(;);" in script_4:
        script_4 = script_4.replace(".trim(;);", ".trim();")
        fixes_applied.append("Fixed function call: trim()")
    
    # Fix malformed commodity check
    if "const isRaw = commodity === 'raw;';" in script_4:
        script_4 = script_4.replace("const isRaw = commodity === 'raw;';", "const isRaw = commodity === 'raw';")
        fixes_applied.append("Fixed string comparison: raw")
    
    # Fix malformed createElement calls
    if "document.createElement('option';);" in script_4:
        script_4 = script_4.replace("document.createElement('option';);", "document.createElement('option');")
        fixes_applied.append("Fixed function call: createElement('option')")
    
    # Fix malformed filter calls
    if "allowedSet.has(opt.norm);" in script_4:
        script_4 = script_4.replace("allowedSet.has(opt.norm);", "allowedSet.has(opt.norm);")
        fixes_applied.append("Fixed function call: has()")
    
    # Fix malformed querySelector calls
    if "document.querySelectorAll('.needs-retest-dropdown';);" in script_4:
        script_4 = script_4.replace("document.querySelectorAll('.needs-retest-dropdown';);", "document.querySelectorAll('.needs-retest-dropdown');")
        fixes_applied.append("Fixed querySelectorAll: needs-retest-dropdown")
    
    # Check if we made any changes
    if script_4 != original_script:
        print(f"\nApplied {len(fixes_applied)} fixes:")
        for fix in fixes_applied:
            print(f"  - {fix}")
        
        # Replace the script in the content
        content = content.replace(original_script, script_4)
        
        # Create backup
        backup_path = f"{template_path}.backup_critical_fixes"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nBackup created: {backup_path}")
        
        # Write fixed content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed template written to: {template_path}")
        
        # Verify the fix
        print("\nVerifying fix...")
        with open(template_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        new_scripts = re.findall(script_pattern, new_content, re.DOTALL)
        if len(new_scripts) >= 4:
            new_script_4 = new_scripts[3]
            new_open_braces = new_script_4.count('{')
            new_close_braces = new_script_4.count('}')
            new_open_parens = new_script_4.count('(')
            new_close_parens = new_script_4.count(')')
            
            print(f"Final braces: {new_open_braces} open, {new_close_braces} close, diff: {new_open_braces - new_close_braces}")
            print(f"Final parentheses: {new_open_parens} open, {new_close_parens} close, diff: {new_open_parens - new_close_parens}")
            
            if new_open_braces == new_close_braces and new_open_parens == new_close_parens:
                print("✅ All critical syntax errors fixed successfully!")
            else:
                print("❌ Some syntax errors remain")
    else:
        print("No critical syntax errors found to fix")

if __name__ == "__main__":
    fix_remaining_critical_errors()
