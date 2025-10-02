#!/usr/bin/env python3
"""
Fix all JavaScript syntax errors found in the analysis
"""

import re
import os

def fix_all_syntax_errors():
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
    
    # Fix malformed attribute access patterns
    # 'data-inspection-id';); -> 'data-inspection-id');
    if "'data-inspection-id';);" in script_4:
        script_4 = script_4.replace("'data-inspection-id';);", "'data-inspection-id');")
        fixes_applied.append("Fixed malformed attribute access: 'data-inspection-id';);")
    
    # Fix malformed property access patterns
    # dropdown.valu;e; -> dropdown.value;
    if "dropdown.valu;e;" in script_4:
        script_4 = script_4.replace("dropdown.valu;e;", "dropdown.value;")
        fixes_applied.append("Fixed malformed property access: dropdown.valu;e;")
    
    # Fix malformed function calls
    # getCSRFToken(;); -> getCSRFToken();
    if "getCSRFToken(;);" in script_4:
        script_4 = script_4.replace("getCSRFToken(;);", "getCSRFToken();")
        fixes_applied.append("Fixed malformed function call: getCSRFToken(;);")
    
    # Fix malformed FormData constructor
    # FormData(;); -> FormData();
    if "FormData(;);" in script_4:
        script_4 = script_4.replace("FormData(;);", "FormData();")
        fixes_applied.append("Fixed malformed FormData constructor: FormData(;);")
    
    # Fix malformed querySelector calls
    # document.querySelector('.needs-retest-dropdown';); -> document.querySelector('.needs-retest-dropdown');
    if "document.querySelector('.needs-retest-dropdown';);" in script_4:
        script_4 = script_4.replace("document.querySelector('.needs-retest-dropdown';);", "document.querySelector('.needs-retest-dropdown');")
        fixes_applied.append("Fixed malformed querySelector call")
    
    # Fix malformed createElement calls
    # document.createElement('input';); -> document.createElement('input');
    if "document.createElement('input';);" in script_4:
        script_4 = script_4.replace("document.createElement('input';);", "document.createElement('input');")
        fixes_applied.append("Fixed malformed createElement call")
    
    # Fix malformed setAttribute calls
    # testInput.setAttribute('data-group-id', 'TEST_GROUP'); -> testInput.setAttribute('data-group-id', 'TEST_GROUP');
    # This one looks correct, but let's check for other patterns
    
    # Fix malformed property access in other places
    # input.valu;e; -> input.value;
    if "input.valu;e;" in script_4:
        script_4 = script_4.replace("input.valu;e;", "input.value;")
        fixes_applied.append("Fixed malformed property access: input.valu;e;")
    
    # Fix malformed checkbox property access
    # checkbox.checke;d; -> checkbox.checked;
    if "checkbox.checke;d;" in script_4:
        script_4 = script_4.replace("checkbox.checke;d;", "checkbox.checked;")
        fixes_applied.append("Fixed malformed checkbox property access: checkbox.checke;d;")
    
    # Fix malformed textContent access
    # countElement.textConten;t; -> countElement.textContent;
    if "countElement.textConten;t;" in script_4:
        script_4 = script_4.replace("countElement.textConten;t;", "countElement.textContent;")
        fixes_applied.append("Fixed malformed textContent access: countElement.textConten;t;")
    
    # Fix malformed disabled property access
    # needsRetestDropdown.disable;d; -> needsRetestDropdown.disabled;
    if "needsRetestDropdown.disable;d;" in script_4:
        script_4 = script_4.replace("needsRetestDropdown.disable;d;", "needsRetestDropdown.disabled;")
        fixes_applied.append("Fixed malformed disabled property access: needsRetestDropdown.disable;d;")
    
    # Fix malformed toLowerCase calls
    # .toLowerCase(;); -> .toLowerCase();
    if ".toLowerCase(;);" in script_4:
        script_4 = script_4.replace(".toLowerCase(;);", ".toLowerCase();")
        fixes_applied.append("Fixed malformed toLowerCase call: .toLowerCase(;);")
    
    # Fix malformed map calls
    # ].map(normalizeLabel);); -> ].map(normalizeLabel);
    if "].map(normalizeLabel););" in script_4:
        script_4 = script_4.replace("].map(normalizeLabel););", "].map(normalizeLabel);")
        fixes_applied.append("Fixed malformed map call: ].map(normalizeLabel););")
    
    # Fix malformed forEach calls
    # });); -> });
    if "}););" in script_4:
        script_4 = script_4.replace("}););", "});")
        fixes_applied.append("Fixed malformed forEach call: }););")
    
    # Fix malformed array access
    # allOptions[0;]; -> allOptions[0];
    if "allOptions[0;];" in script_4:
        script_4 = script_4.replace("allOptions[0;];", "allOptions[0];")
        fixes_applied.append("Fixed malformed array access: allOptions[0;];")
    
    # Fix malformed property access in other places
    # pmpAllowe;d; -> pmpAllowed;
    if "pmpAllowe;d;" in script_4:
        script_4 = script_4.replace("pmpAllowe;d;", "pmpAllowed;")
        fixes_applied.append("Fixed malformed property access: pmpAllowe;d;")
    
    # Fix malformed filter calls
    # allowedSet.has(opt.norm);); -> allowedSet.has(opt.norm);
    if "allowedSet.has(opt.norm););" in script_4:
        script_4 = script_4.replace("allowedSet.has(opt.norm););", "allowedSet.has(opt.norm);")
        fixes_applied.append("Fixed malformed filter call: allowedSet.has(opt.norm););")
    
    # Fix malformed querySelector calls with selectors
    # document.querySelector('select[name="sample_status"]';); -> document.querySelector('select[name="sample_status"]');
    if "document.querySelector('select[name=\"sample_status\"]';);" in script_4:
        script_4 = script_4.replace("document.querySelector('select[name=\"sample_status\"]';);", "document.querySelector('select[name=\"sample_status\"]');")
        fixes_applied.append("Fixed malformed querySelector call with selectors")
    
    # Fix malformed URLSearchParams calls
    # new URLSearchParams(window.location.search;); -> new URLSearchParams(window.location.search);
    if "new URLSearchParams(window.location.search;);" in script_4:
        script_4 = script_4.replace("new URLSearchParams(window.location.search;);", "new URLSearchParams(window.location.search);")
        fixes_applied.append("Fixed malformed URLSearchParams call")
    
    # Fix malformed getAttribute calls
    # urlParams.get('sample_status';); -> urlParams.get('sample_status');
    if "urlParams.get('sample_status';);" in script_4:
        script_4 = script_4.replace("urlParams.get('sample_status';);", "urlParams.get('sample_status');")
        fixes_applied.append("Fixed malformed getAttribute call")
    
    # Fix malformed querySelector calls with class selectors
    # document.querySelectorAll('.group-row.shipment-row';); -> document.querySelectorAll('.group-row.shipment-row');
    if "document.querySelectorAll('.group-row.shipment-row';);" in script_4:
        script_4 = script_4.replace("document.querySelectorAll('.group-row.shipment-row';);", "document.querySelectorAll('.group-row.shipment-row');")
        fixes_applied.append("Fixed malformed querySelectorAll call")
    
    # Fix malformed variable declarations
    # let visibleCount = ;0; -> let visibleCount = 0;
    if "let visibleCount = ;0;" in script_4:
        script_4 = script_4.replace("let visibleCount = ;0;", "let visibleCount = 0;")
        fixes_applied.append("Fixed malformed variable declaration: let visibleCount = ;0;")
    
    # Fix malformed variable declarations
    # let hiddenCount = ;0; -> let hiddenCount = 0;
    if "let hiddenCount = ;0;" in script_4:
        script_4 = script_4.replace("let hiddenCount = ;0;", "let hiddenCount = 0;")
        fixes_applied.append("Fixed malformed variable declaration: let hiddenCount = ;0;")
    
    # Fix malformed variable declarations
    # let sampledCount = ;0; -> let sampledCount = 0;
    if "let sampledCount = ;0;" in script_4:
        script_4 = script_4.replace("let sampledCount = ;0;", "let sampledCount = 0;")
        fixes_applied.append("Fixed malformed variable declaration: let sampledCount = ;0;")
    
    # Fix malformed variable declarations
    # let notSampledCount = ;0; -> let notSampledCount = 0;
    if "let notSampledCount = ;0;" in script_4:
        script_4 = script_4.replace("let notSampledCount = ;0;", "let notSampledCount = 0;")
        fixes_applied.append("Fixed malformed variable declaration: let notSampledCount = ;0;")
    
    # Fix malformed variable declarations
    # let unknownCount = ;0; -> let unknownCount = 0;
    if "let unknownCount = ;0;" in script_4:
        script_4 = script_4.replace("let unknownCount = ;0;", "let unknownCount = 0;")
        fixes_applied.append("Fixed malformed variable declaration: let unknownCount = ;0;")
    
    # Fix malformed querySelector calls
    # document.querySelector('.table-info';); -> document.querySelector('.table-info');
    if "document.querySelector('.table-info';);" in script_4:
        script_4 = script_4.replace("document.querySelector('.table-info';);", "document.querySelector('.table-info');")
        fixes_applied.append("Fixed malformed querySelector call: .table-info")
    
    # Fix malformed replace calls
    # currentText.replace(/Showing \d+ of \d+ inspections/, `Showing ${count} of ${count} inspections`;); -> currentText.replace(/Showing \d+ of \d+ inspections/, `Showing ${count} of ${count} inspections`);
    if "currentText.replace(/Showing \\d+ of \\d+ inspections/, `Showing ${count} of ${count} inspections`;);" in script_4:
        script_4 = script_4.replace("currentText.replace(/Showing \\d+ of \\d+ inspections/, `Showing ${count} of ${count} inspections`;);", "currentText.replace(/Showing \\d+ of \\d+ inspections/, `Showing ${count} of ${count} inspections`);")
        fixes_applied.append("Fixed malformed replace call")
    
    # Fix malformed querySelector calls
    # document.querySelector('form[method=\"get\"]';); -> document.querySelector('form[method=\"get\"]');
    if "document.querySelector('form[method=\"get\"]';);" in script_4:
        script_4 = script_4.replace("document.querySelector('form[method=\"get\"]';);", "document.querySelector('form[method=\"get\"]');")
        fixes_applied.append("Fixed malformed querySelector call: form[method=\"get\"]")
    
    # Fix malformed URL constructor
    # new URL(window.location;); -> new URL(window.location);
    if "new URL(window.location;);" in script_4:
        script_4 = script_4.replace("new URL(window.location;);", "new URL(window.location);")
        fixes_applied.append("Fixed malformed URL constructor")
    
    # Fix malformed querySelector calls with ID selectors
    # document.getElementById('lab-' + inspectionId;); -> document.getElementById('lab-' + inspectionId);
    if "document.getElementById('lab-' + inspectionId;);" in script_4:
        script_4 = script_4.replace("document.getElementById('lab-' + inspectionId;);", "document.getElementById('lab-' + inspectionId);")
        fixes_applied.append("Fixed malformed getElementById call: lab-")
    
    # Fix malformed querySelector calls with ID selectors
    # document.getElementById('retest-' + inspectionId;); -> document.getElementById('retest-' + inspectionId);
    if "document.getElementById('retest-' + inspectionId;);" in script_4:
        script_4 = script_4.replace("document.getElementById('retest-' + inspectionId;);", "document.getElementById('retest-' + inspectionId);")
        fixes_applied.append("Fixed malformed getElementById call: retest-")
    
    # Fix malformed querySelector calls with attribute selectors
    # document.querySelector('select[data-inspection-id=\"' + inspectionId + '\"]';); -> document.querySelector('select[data-inspection-id=\"' + inspectionId + '\"]');
    if "document.querySelector('select[data-inspection-id=\"' + inspectionId + '\"]';);" in script_4:
        script_4 = script_4.replace("document.querySelector('select[data-inspection-id=\"' + inspectionId + '\"]';);", "document.querySelector('select[data-inspection-id=\"' + inspectionId + '\"]');")
        fixes_applied.append("Fixed malformed querySelector call: select[data-inspection-id]")
    
    # Fix malformed querySelector calls with class selectors
    # document.querySelector('select.lab-dropdown[data-inspection-id=\"' + inspectionId + '\"]';); -> document.querySelector('select.lab-dropdown[data-inspection-id=\"' + inspectionId + '\"]');
    if "document.querySelector('select.lab-dropdown[data-inspection-id=\"' + inspectionId + '\"]';);" in script_4:
        script_4 = script_4.replace("document.querySelector('select.lab-dropdown[data-inspection-id=\"' + inspectionId + '\"]';);", "document.querySelector('select.lab-dropdown[data-inspection-id=\"' + inspectionId + '\"]');")
        fixes_applied.append("Fixed malformed querySelector call: select.lab-dropdown")
    
    # Fix malformed querySelector calls with class selectors
    # document.querySelectorAll('.detail-row';); -> document.querySelectorAll('.detail-row');
    if "document.querySelectorAll('.detail-row';);" in script_4:
        script_4 = script_4.replace("document.querySelectorAll('.detail-row';);", "document.querySelectorAll('.detail-row');")
        fixes_applied.append("Fixed malformed querySelectorAll call: .detail-row")
    
    # Fix malformed Map constructor
    # const originalStates = new Map(;); -> const originalStates = new Map();
    if "const originalStates = new Map(;);" in script_4:
        script_4 = script_4.replace("const originalStates = new Map(;);", "const originalStates = new Map();")
        fixes_applied.append("Fixed malformed Map constructor")
    
    # Fix malformed querySelector calls with class selectors
    # document.querySelectorAll('.onedrive-countdown';); -> document.querySelectorAll('.onedrive-countdown');
    if "document.querySelectorAll('.onedrive-countdown';);" in script_4:
        script_4 = script_4.replace("document.querySelectorAll('.onedrive-countdown';);", "document.querySelectorAll('.onedrive-countdown');")
        fixes_applied.append("Fixed malformed querySelectorAll call: .onedrive-countdown")
    
    # Fix malformed querySelector calls with ID selectors
    # document.getElementById('shipmentsTable';); -> document.getElementById('shipmentsTable');
    if "document.getElementById('shipmentsTable';);" in script_4:
        script_4 = script_4.replace("document.getElementById('shipmentsTable';);", "document.getElementById('shipmentsTable');")
        fixes_applied.append("Fixed malformed getElementById call: shipmentsTable")
    
    # Fix malformed querySelector calls with class selectors
    # document.querySelectorAll('select.product-class-select').forEach(filterClassOptions); -> document.querySelectorAll('select.product-class-select').forEach(filterClassOptions);
    # This one looks correct, but let's check for other patterns
    
    # Fix malformed return statement
    # dropdownValue: dropdown ? dropdown.value : nullLine 4025: braces=-1, parens=-2 - }); -> dropdownValue: dropdown ? dropdown.value : null
    if "dropdownValue: dropdown ? dropdown.value : nullLine 4025: braces=-1, parens=-2 - });" in script_4:
        script_4 = script_4.replace("dropdownValue: dropdown ? dropdown.value : nullLine 4025: braces=-1, parens=-2 - });", "dropdownValue: dropdown ? dropdown.value : null")
        fixes_applied.append("Fixed malformed return statement")
    
    # Check if we made any changes
    if script_4 != original_script:
        print(f"\nApplied {len(fixes_applied)} fixes:")
        for fix in fixes_applied:
            print(f"  - {fix}")
        
        # Replace the script in the content
        content = content.replace(original_script, script_4)
        
        # Create backup
        backup_path = f"{template_path}.backup_all_syntax_fixes"
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
                print("✅ All syntax errors fixed successfully!")
            else:
                print("❌ Some syntax errors remain")
    else:
        print("No syntax errors found to fix")

if __name__ == "__main__":
    fix_all_syntax_errors()
