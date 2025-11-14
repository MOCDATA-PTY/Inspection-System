"""
ODBC Driver 18 Testing and Installation Script
This script will:
1. Check if ODBC Driver 18 is installed
2. If not, download and install it
3. Test SQL Server connection with Driver 18
4. Verify everything works before updating the application
"""

import pyodbc
import subprocess
import os
import sys
import urllib.request
import tempfile
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def check_driver_installed(driver_name):
    """Check if a specific ODBC driver is installed"""
    drivers = [x for x in pyodbc.drivers() if driver_name.lower() in x.lower()]
    return len(drivers) > 0, drivers

def list_all_drivers():
    """List all available ODBC drivers"""
    print("\n" + "="*70)
    print("AVAILABLE ODBC DRIVERS")
    print("="*70)
    drivers = pyodbc.drivers()
    for i, driver in enumerate(drivers, 1):
        print(f"{i}. {driver}")
    print("="*70 + "\n")
    return drivers

def download_and_install_driver18():
    """Download and install ODBC Driver 18 for SQL Server"""
    print("\n" + "="*70)
    print("INSTALLING ODBC DRIVER 18 FOR SQL SERVER")
    print("="*70)

    # Download URL for ODBC Driver 18
    download_url = "https://go.microsoft.com/fwlink/?linkid=2249004"

    print(f"\nDownloading ODBC Driver 18 from Microsoft...")
    print(f"URL: {download_url}")

    try:
        # Download to temp directory
        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, "msodbcsql.msi")

        print(f"Downloading to: {installer_path}")
        urllib.request.urlretrieve(download_url, installer_path)
        print("✓ Download complete!")

        # Install using msiexec
        print("\nInstalling ODBC Driver 18...")
        print("This may take a few minutes. Please wait...")

        install_command = [
            "msiexec.exe",
            "/i", installer_path,
            "IACCEPTMSODBCSQLLICENSETERMS=YES",
            "/quiet",
            "/norestart"
        ]

        result = subprocess.run(install_command, capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ ODBC Driver 18 installed successfully!")
            print("\nPlease restart this script to verify the installation.")
            return True
        else:
            print(f"✗ Installation failed with return code: {result.returncode}")
            print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Error during installation: {str(e)}")
        print("\nPlease install ODBC Driver 18 manually from:")
        print("https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
        return False

def test_sql_server_connection(driver_name):
    """Test SQL Server connection with specified driver"""
    print("\n" + "="*70)
    print(f"TESTING SQL SERVER CONNECTION WITH {driver_name}")
    print("="*70)

    # SQL Server connection details from settings.py
    server = "102.67.140.12"
    port = "1053"
    database = "AFS"
    username = "FSAUser2"
    password = "password"
    timeout = 5

    print(f"\nConnection Details:")
    print(f"  Server: {server}")
    print(f"  Port: {port}")
    print(f"  Database: {database}")
    print(f"  Username: {username}")
    print(f"  Driver: {driver_name}")
    print(f"  Timeout: {timeout} seconds")

    # Build connection string
    # Note: TrustServerCertificate=yes is needed for Driver 18 to bypass SSL cert validation
    connection_string = (
        f"DRIVER={{{driver_name}}};"
        f"SERVER={server},{port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Connection Timeout={timeout};"
        f"TrustServerCertificate=yes;"
    )

    print(f"\nAttempting connection...")

    try:
        # Test connection
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Test query
        cursor.execute("SELECT 1 AS test")
        result = cursor.fetchone()

        print(f"✓ Connection successful!")
        print(f"✓ Test query executed successfully")
        print(f"✓ Result: {result[0]}")

        # Get SQL Server version
        cursor.execute("SELECT @@VERSION AS version")
        version = cursor.fetchone()
        print(f"\nSQL Server Version:")
        print(f"  {version[0][:100]}...")

        cursor.close()
        conn.close()

        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED - DRIVER 18 WORKS PERFECTLY!")
        print("="*70)
        return True

    except pyodbc.Error as e:
        print(f"\n✗ Connection failed!")
        print(f"Error: {str(e)}")
        print("\n" + "="*70)
        return False

def main():
    """Main function to run all tests"""
    print("\n" + "="*70)
    print("ODBC DRIVER 18 INSTALLATION AND TESTING")
    print("="*70)

    # Step 1: List all available drivers
    all_drivers = list_all_drivers()

    # Step 2: Check for Driver 17
    print("Checking for ODBC Driver 17 for SQL Server...")
    has_driver17, driver17_list = check_driver_installed("ODBC Driver 17 for SQL Server")
    if has_driver17:
        print(f"✓ Driver 17 found: {driver17_list}")
    else:
        print("✗ Driver 17 not found")

    # Step 3: Check for Driver 18
    print("\nChecking for ODBC Driver 18 for SQL Server...")
    has_driver18, driver18_list = check_driver_installed("ODBC Driver 18 for SQL Server")

    if has_driver18:
        print(f"✓ Driver 18 found: {driver18_list}")
        driver18_name = driver18_list[0]
    else:
        print("✗ Driver 18 not found")
        print("\nAttempting to install ODBC Driver 18 automatically...")

        success = download_and_install_driver18()
        if success:
            print("\nInstallation complete. Please restart this script.")
            return
        else:
            print("\nInstallation failed. Please install manually and restart this script.")
            return

    # Step 4: Test connection with Driver 18
    if has_driver18:
        driver18_name = driver18_list[0]
        success = test_sql_server_connection(driver18_name)

        if success:
            print("\n" + "="*70)
            print("NEXT STEPS:")
            print("="*70)
            print("1. Driver 18 is installed and working perfectly")
            print("2. Ready to update application code to use Driver 18")
            print("3. Files to update:")
            print("   - mysite/settings.py")
            print("   - main/utils/sql_server_utils.py")
            print("   - main/views/data_views.py")
            print("   - sql_server_connection.py")
            print("   - production_server_diagnostic.py")
            print("\nYou can now proceed with updating the code!")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("CONNECTION TEST FAILED")
            print("="*70)
            print("Please check:")
            print("1. SQL Server is accessible from this machine")
            print("2. Firewall allows connection to 102.67.140.12:1053")
            print("3. Credentials are correct")
            print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
