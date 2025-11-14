"""
Test script to check if /page-clients-status/ endpoint returns correct data for mobile cards
"""
import requests
import json
from datetime import datetime

# Django server URL (adjust if needed)
BASE_URL = "http://localhost:8000"
ENDPOINT = "/page-clients-status/"

# Test credentials (adjust to match your test user)
USERNAME = "developer"
PASSWORD = "Ethan4269875321"

def test_page_clients_status():
    """Test the /page-clients-status/ endpoint with mobile card data"""

    print("=" * 80)
    print("TESTING /page-clients-status/ ENDPOINT")
    print("=" * 80)

    # Create a session to maintain login
    session = requests.Session()

    # Step 1: Get CSRF token from login page
    print("\n[1] Getting CSRF token from login page...")
    login_page = session.get(f"{BASE_URL}/login/")
    csrf_token = None

    # Extract CSRF token from cookies
    if 'csrftoken' in session.cookies:
        csrf_token = session.cookies['csrftoken']
        print(f"    [OK] CSRF token obtained: {csrf_token[:20]}...")
    else:
        print("    [ERROR] Failed to get CSRF token")
        return

    # Step 2: Login
    print(f"\n[2] Logging in as '{USERNAME}'...")
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token
    }
    login_response = session.post(
        f"{BASE_URL}/login/",
        data=login_data,
        headers={'Referer': f"{BASE_URL}/login/"}
    )

    if login_response.status_code == 200 or 'sessionid' in session.cookies:
        print("    [OK] Login successful")
    else:
        print(f"    [ERROR] Login failed (status: {login_response.status_code})")
        return

    # Step 3: Prepare test data (simulating mobile card data)
    print("\n[3] Preparing test client+date combinations...")

    # Test with recent dates (adjust these to match your actual data)
    test_combinations = [
        {
            "client_name": "Beckley Brothers Poultry Farm",
            "inspection_date": "2025-11-07",
            "unique_key": "Beckley Brothers Poultry Farm_2025-11-07"
        },
        {
            "client_name": "Beckley Brothers Poultry Farm",
            "inspection_date": "2025-11-06",
            "unique_key": "Beckley Brothers Poultry Farm_2025-11-06"
        }
    ]

    print(f"    Test combinations ({len(test_combinations)} total):")
    for combo in test_combinations:
        print(f"      - {combo['unique_key']}")

    # Step 4: Send POST request to endpoint
    print(f"\n[4] Sending POST request to {ENDPOINT}...")

    # Update CSRF token from cookies
    if 'csrftoken' in session.cookies:
        csrf_token = session.cookies['csrftoken']

    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,
        'Referer': f"{BASE_URL}/inspections/"
    }

    payload = {
        'client_date_combinations': test_combinations
    }

    print(f"    Payload: {json.dumps(payload, indent=2)}")

    try:
        response = session.post(
            f"{BASE_URL}{ENDPOINT}",
            json=payload,
            headers=headers
        )

        print(f"\n[5] Response received (status: {response.status_code})")

        if response.status_code == 200:
            print("    [OK] Request successful (200 OK)")

            # Show raw response first
            print(f"\n    Raw response text (first 1000 chars):")
            print(f"    {response.text[:1000]}")

            # Parse JSON response
            try:
                data = response.json()
                print("\n[6] Response data:")
                print(json.dumps(data, indent=2))

                # Analyze response
                print("\n[7] Analysis:")
                print(f"    Success: {data.get('success', False)}")
                print(f"    Total checked: {data.get('total_checked', 0)}")
                print(f"    Source: {data.get('source', 'unknown')}")

                if 'combination_statuses' in data:
                    print(f"\n    Combination statuses ({len(data['combination_statuses'])} found):")
                    for key, status in data['combination_statuses'].items():
                        print(f"\n      {key}:")
                        print(f"        - Client: {status.get('client_name')}")
                        print(f"        - Date: {status.get('inspection_date')}")
                        print(f"        - File Status: {status.get('file_status')}")
                        print(f"        - Has RFI: {status.get('has_rfi')}")
                        print(f"        - Has Invoice: {status.get('has_invoice')}")
                        print(f"        - Has Lab: {status.get('has_lab')}")
                        print(f"        - Has Compliance: {status.get('has_compliance')}")

                # Check for expected data
                print("\n[8] Verification:")
                beckley_2025_11_07 = data.get('combination_statuses', {}).get('Beckley Brothers Poultry Farm_2025-11-07')
                if beckley_2025_11_07:
                    print("    [OK] Found 'Beckley Brothers Poultry Farm_2025-11-07' in response")
                    print(f"      File Status: {beckley_2025_11_07.get('file_status')}")
                    print(f"      Has RFI: {beckley_2025_11_07.get('has_rfi')}")
                    print(f"      Has Invoice: {beckley_2025_11_07.get('has_invoice')}")
                else:
                    print("    [ERROR] 'Beckley Brothers Poultry Farm_2025-11-07' NOT found in response")
                    print("      This means the backend is not returning data for this combination")

            except json.JSONDecodeError as e:
                print(f"    [ERROR] Failed to parse JSON response: {e}")
                print(f"    Raw response: {response.text[:500]}")
        else:
            print(f"    [ERROR] Request failed (status: {response.status_code})")
            print(f"    Response: {response.text[:500]}")

    except requests.RequestException as e:
        print(f"    [ERROR] Request error: {e}")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_page_clients_status()
