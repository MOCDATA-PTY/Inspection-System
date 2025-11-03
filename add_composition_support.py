"""
Script to add Composition document support to the inspection system
This script modifies core_views.py to add composition upload functionality
"""
import re

# Path to core_views.py
FILE_PATH = "main/views/core_views.py"

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def add_composition_support():
    print("Reading core_views.py...")
    content = read_file(FILE_PATH)
    original_content = content
    
    # 1. Update administrator allowed document types
    print("1. Adding composition to administrator allowed documents...")
    content = re.sub(
        r"allowed_document_types = \['invoice', 'rfi'\]",
        r"allowed_document_types = ['invoice', 'rfi', 'composition']",
        content
    )
    content = re.sub(
        r"'error': 'Access denied\. Administrators can only upload invoice and RFI documents\.'",
        r"'error': 'Access denied. Administrators can only upload invoice, RFI, and composition documents.'",
        content
    )
    
    # 2. Add composition to document type handling (folder mapping)
    print("2. Adding composition to folder maps...")
    
    # Add to individual inspection folder map
    content = re.sub(
        r"(\s+)'occurrence': 'occurrence'(\s+# Occurrence documents.*?\n\s+})",
        r"\1'occurrence': 'occurrence',\2\n\1'composition': 'composition'  # Composition documents go to 'composition' folder (lowercase)\n\1}",
        content,
        flags=re.MULTILINE
    )
    
    # Add to top-level folder map  
    content = re.sub(
        r"(\s+)'occurrence': 'occurrence',?\n(\s+)",
        r"\1'occurrence': 'occurrence',\n\1'composition': 'composition',\n\2",
        content
    )
    
    # 3. Add composition to if condition check
    print("3. Adding composition to document type conditions...")
    content = re.sub(
        r"if document_type in \['rfi', 'invoice', 'compliance', 'lab', 'lab_form', 'retest', 'form', 'occurrence'\]:",
        r"if document_type in ['rfi', 'invoice', 'compliance', 'lab', 'lab_form', 'retest', 'form', 'occurrence', 'composition']:",
        content
    )
    
    # 4. Add composition tracking fields update
    print("4. Adding composition upload tracking...")
    
    # For group uploads
    composition_group_update = '''                                elif document_type == 'composition':
                                    updated_count = group_inspections.update(
                                        composition_uploaded_by=request.user,
                                        composition_uploaded_date=current_time
                                    )
                                    print(f"DEBUG: Updated Composition tracking for {updated_count} inspections")
                                '''
    
    # Find the occurrence group update and add composition after it
    content = re.sub(
        r"(elif document_type == 'occurrence':.*?print\(f\"DEBUG: Updated Occurrence tracking.*?\n)",
        r"\1" + composition_group_update,
        content,
        flags=re.DOTALL
    )
    
    # For individual uploads
    composition_individual_update = '''                    elif document_type == 'composition':
                        inspection.composition_uploaded_by = request.user
                        inspection.composition_uploaded_date = current_time
                        inspection.save(update_fields=['composition_uploaded_by', 'composition_uploaded_date'])
                        print(f"DEBUG: Updated Composition tracking for individual inspection {inspection_id}")
                    '''
    
    # Find the occurrence individual update and add composition after it
    content = re.sub(
        r"(elif document_type == 'occurrence':.*?print\(f\"DEBUG: Updated Occurrence tracking for individual inspection.*?\n)",
        r"\1" + composition_individual_update,
        content,
        flags=re.DOTALL
    )
    
    # Check if changes were made
    if content == original_content:
        print("WARNING: No changes were made. File might already have composition support or patterns don't match.")
        return False
    
    # Write the modified content
    print("Writing changes to core_views.py...")
    write_file(FILE_PATH, content)
    
    print("\n✅ Composition support added successfully!")
    print("\nChanges made:")
    print("  - Added 'composition' to administrator allowed document types")
    print("  - Added 'composition' folder mapping for file uploads")
    print("  - Added composition_uploaded_by and composition_uploaded_date tracking")
    print("  - Added composition to document type conditions")
    
    return True

if __name__ == '__main__':
    try:
        add_composition_support()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
