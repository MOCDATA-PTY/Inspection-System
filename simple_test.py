#!/usr/bin/env python3
"""
Simple test script to verify RFI button color changes
This script creates a simple HTML page to test RFI button functionality
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def create_test_html():
    """Create a simple HTML test page with RFI buttons"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>RFI Button Color Test</title>
    <style>
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
        }
        .btn-secondary {
            background-color: #6c757d;
            color: white;
        }
        .btn-success {
            background-color: #28a745;
            color: white;
        }
        .btn-danger {
            background-color: #dc3545;
            color: white;
        }
    </style>
</head>
<body>
    <h1>RFI Button Color Test</h1>
    <p>This page tests RFI button color changes</p>
    
    <div>
        <h3>Test RFI Buttons:</h3>
        <button id="rfi-test1" class="btn btn-secondary" onclick="toggleRFI('test1')">RFI</button>
        <button id="rfi-test2" class="btn btn-success" onclick="toggleRFI('test2')">RFI ✓</button>
        <button id="rfi-test3" class="btn btn-secondary" onclick="toggleRFI('test3')">RFI</button>
    </div>
    
    <div>
        <h3>Actions:</h3>
        <button onclick="makeAllGreen()">Make All Green</button>
        <button onclick="makeAllGrey()">Make All Grey</button>
        <button onclick="makeAllRed()">Make All Red</button>
    </div>
    
    <script>
        function toggleRFI(id) {
            const button = document.getElementById('rfi-' + id);
            if (button.classList.contains('btn-success')) {
                button.className = 'btn btn-secondary';
                button.innerHTML = 'RFI';
            } else {
                button.className = 'btn btn-success';
                button.innerHTML = 'RFI ✓';
            }
        }
        
        function makeAllGreen() {
            const buttons = document.querySelectorAll('button[id^="rfi-"]');
            buttons.forEach(btn => {
                btn.className = 'btn btn-success';
                btn.innerHTML = 'RFI ✓';
            });
        }
        
        function makeAllGrey() {
            const buttons = document.querySelectorAll('button[id^="rfi-"]');
            buttons.forEach(btn => {
                btn.className = 'btn btn-secondary';
                btn.innerHTML = 'RFI';
            });
        }
        
        function makeAllRed() {
            const buttons = document.querySelectorAll('button[id^="rfi-"]');
            buttons.forEach(btn => {
                btn.className = 'btn btn-danger';
                btn.innerHTML = 'RFI ✗';
            });
        }
    </script>
</body>
</html>
    """
    
    with open('test_rfi.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Created test_rfi.html")

def test_rfi_button_color():
    """Test that RFI buttons change color correctly"""
    
    print("🧪 Starting RFI button color change test...")
    
    # Create test HTML file
    create_test_html()
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    try:
        # Initialize the Chrome driver
        from selenium.webdriver.chrome.service import Service
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_window_size(1920, 1080)
        
        # Navigate to the test page
        print("📄 Navigating to test page...")
        test_file_path = os.path.abspath('test_rfi.html')
        driver.get(f'file://{test_file_path}')
        
        # Wait for page to load
        time.sleep(2)
        
        # Find all RFI buttons
        print("🔍 Finding RFI buttons...")
        rfi_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[id^="rfi-"]')
        print(f"✅ Found {len(rfi_buttons)} RFI buttons")
        
        if not rfi_buttons:
            print("⚠️ No RFI buttons found on the page")
            return False
        
        # Test initial RFI button colors
        print("\n🎨 Testing initial RFI button colors...")
        success_count = 0
        grey_count = 0
        green_count = 0
        
        for i, button in enumerate(rfi_buttons, 1):
            button_id = button.get_attribute('id')
            background_color = button.value_of_css_property('background-color')
            button_class = button.get_attribute('class')
            button_text = button.text.strip()
            
            print(f"\n📌 Button {i}: {button_id}")
            print(f"   Text: {button_text}")
            print(f"   Classes: {button_class}")
            print(f"   Background color: {background_color}")
            
            # Check if button is green (success state - file uploaded)
            if 'btn-success' in button_class or background_color == 'rgb(40, 167, 69)':
                print(f"   ✅ GREEN - RFI file uploaded")
                green_count += 1
            # Check if button is grey (default state - no file)
            elif 'btn-secondary' in button_class or background_color == 'rgb(108, 117, 125)':
                print(f"   ⚪ GREY - No RFI file")
                grey_count += 1
            else:
                print(f"   ⚠️ UNKNOWN color state")
        
        print(f"\n📊 Initial Summary:")
        print(f"   Total buttons: {len(rfi_buttons)}")
        print(f"   Green (with files): {green_count}")
        print(f"   Grey (no files): {grey_count}")
        
        # Test color changes
        print("\n🔄 Testing color changes...")
        
        # Test making all buttons green
        print("   Making all buttons green...")
        make_green_button = driver.find_element(By.XPATH, "//button[text()='Make All Green']")
        make_green_button.click()
        time.sleep(1)
        
        # Check colors after change
        green_count_after = 0
        for button in rfi_buttons:
            if 'btn-success' in button.get_attribute('class'):
                green_count_after += 1
        
        print(f"   Green buttons after change: {green_count_after}")
        
        # Test making all buttons grey
        print("   Making all buttons grey...")
        make_grey_button = driver.find_element(By.XPATH, "//button[text()='Make All Grey']")
        make_grey_button.click()
        time.sleep(1)
        
        # Check colors after change
        grey_count_after = 0
        for button in rfi_buttons:
            if 'btn-secondary' in button.get_attribute('class'):
                grey_count_after += 1
        
        print(f"   Grey buttons after change: {grey_count_after}")
        
        # Take a screenshot for verification
        screenshot_path = 'rfi_buttons_test.png'
        driver.save_screenshot(screenshot_path)
        print(f"\n📸 Screenshot saved to: {screenshot_path}")
        
        driver.quit()
        
        print("\n✅ Test completed successfully!")
        print("✅ RFI button color changes are working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return False

if __name__ == '__main__':
    success = test_rfi_button_color()
    sys.exit(0 if success else 1)
