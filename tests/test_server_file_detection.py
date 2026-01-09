"""
Test the file detection fix on the server by making a direct API call.
This will help us verify if the sanitization is working correctly.
"""

import requests
import json

# Test the server endpoint directly
server_url = "http://82.25.97.159"

# Test data
test_data = {
    'client_name': 'Boxer Superstore - Kwamashu 2',
    'inspection_date': '2025-09-26'
}

print("=" * 80)
print("TESTING SERVER FILE DETECTION FIX")
print("=" * 80)

print(f"\n1. Testing client: {test_data['client_name']} on {test_data['inspection_date']}")
print(f"   Expected sanitized name: Boxer_Superstore_Kwamashu_2")

# Test the list_client_folder_files endpoint
print("\n2. Calling list_client_folder_files endpoint...")
try:
    response = requests.post(
        f"{server_url}/list-client-folder-files/",
        data=json.dumps(test_data),
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    print(f"   Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Files found: {data.get('files', {})}")
        
        files = data.get('files', {})
        rfi_files = files.get('rfi', [])
        invoice_files = files.get('invoice', [])
        lab_files = files.get('lab', [])
        compliance_files = files.get('compliance', [])
        
        print(f"\n   RFI files: {len(rfi_files)}")
        print(f"   Invoice files: {len(invoice_files)}")
        print(f"   Lab files: {len(lab_files)}")
        print(f"   Compliance files: {len(compliance_files)}")
        
        if rfi_files:
            print(f"\n   ✅ RFI files found:")
            for f in rfi_files:
                print(f"     - {f.get('name')}")
        else:
            print(f"\n   ❌ No RFI files found!")
            
        # Check if there are any files at all
        total_files = len(rfi_files) + len(invoice_files) + len(lab_files) + len(compliance_files)
        if total_files > 0:
            print(f"\n   ✅ Total files found: {total_files}")
        else:
            print(f"\n   ❌ No files found at all!")
            
    else:
        print(f"   ERROR: {response.text}")
        
except Exception as e:
    print(f"   ERROR: {e}")

# Test the get_page_clients_file_status endpoint
print("\n3. Calling get_page_clients_file_status endpoint...")
try:
    response = requests.post(
        f"{server_url}/page-clients-status/",
        data=json.dumps({
            'client_date_combinations': [{
                'client_name': test_data['client_name'],
                'inspection_date': test_data['inspection_date'],
                'unique_key': f'{test_data["client_name"]}_{test_data["inspection_date"]}'
            }]
        }),
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    print(f"   Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        
        combination_statuses = data.get('combination_statuses', {})
        for key, status in combination_statuses.items():
            print(f"\n   Status for {key}:")
            print(f"     File status: {status.get('file_status')}")
            print(f"     Has RFI: {status.get('has_rfi')}")
            print(f"     Has Invoice: {status.get('has_invoice')}")
            print(f"     Has Lab: {status.get('has_lab')}")
            print(f"     Has Compliance: {status.get('has_compliance')}")
    else:
        print(f"   ERROR: {response.text}")
        
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
