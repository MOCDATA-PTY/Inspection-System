def scan_inspection_folders(test_path, seen_files):
    """Scan Inspection-XXXX folders for files and return a list of files by category."""
    files_list = {}
    inspection_folders = [d for d in os.listdir(test_path) if d.startswith('Inspection-') and os.path.isdir(os.path.join(test_path, d))]
    
    for inspection_folder in sorted(inspection_folders):
        inspection_path = os.path.join(test_path, inspection_folder)
        print(f"🔍 [DEBUG] Checking inspection folder: {inspection_folder}")
        
        # Check each document type in the inspection folder
        doc_types = ['Request For Invoice', 'invoice', 'lab results', 'retest', 'Compliance']
        for doc_type in doc_types:
            doc_path = os.path.join(inspection_path, doc_type)
            if os.path.exists(doc_path):
                print(f"🔍 [DEBUG] Found {doc_type} in {inspection_folder}")
                files = []
                
                # Handle subfolders (for lab results and compliance)
                paths_to_check = []
                if doc_type in ['lab results', 'Compliance']:
                    # Check commodity subfolders
                    for item in os.listdir(doc_path):
                        item_path = os.path.join(doc_path, item)
                        if os.path.isdir(item_path):
                            paths_to_check.append(item_path)
                            print(f"🔍 [DEBUG] Adding commodity path: {item_path}")
                else:
                    paths_to_check = [doc_path]
                
                # Scan all paths for files
                for check_path in paths_to_check:
                    try:
                        for filename in os.listdir(check_path):
                            file_path = os.path.join(check_path, filename)
                            if os.path.isfile(file_path):
                                file_size = os.path.getsize(file_path)
                                unique_key = (filename, file_size, os.path.getmtime(file_path))
                                
                                if unique_key not in seen_files:
                                    seen_files.add(unique_key)
                                    display_path = os.path.join(inspection_folder, doc_type, os.path.relpath(file_path, doc_path))
                                    files.append({
                                        'name': filename,
                                        'path': display_path.replace('\\', '/'),
                                        'size': file_size
                                    })
                                    print(f"✅ [DEBUG] Added file: {filename} from {doc_type}")
                    except Exception as e:
                        print(f"⚠️ Error reading files in {check_path}: {e}")
                
                if files:
                    # Use standardized category keys
                    category_key = doc_type.lower()
                    if doc_type == 'Request For Invoice':
                        category_key = 'rfi'
                    elif doc_type == 'lab results':
                        category_key = 'lab'
                    elif doc_type == 'Compliance':
                        category_key = 'compliance'
                    
                    if category_key not in files_list:
                        files_list[category_key] = []
                    files_list[category_key].extend(files)
    
    return files_list
