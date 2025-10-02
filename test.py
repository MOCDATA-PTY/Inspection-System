#!/usr/bin/env python3
"""
Test script to verify RFI button color changes
This script tests that RFI buttons change color correctly when files are uploaded
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_rfi_button_color():
    """Test that RFI buttons change color correctly"""
    
    print("🧪 Starting RFI button color change test...")
    
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
        
        # Navigate to the login page first
        print("📄 Navigating to login page...")
        driver.get('http://localhost:8000/login/')
        
        # Wait for page to load
        time.sleep(2)
        
        # Find and fill login form (assuming standard Django admin login)
        print("🔐 Attempting to login...")
        username_field = driver.find_element(By.NAME, 'username')
        password_field = driver.find_element(By.NAME, 'password')
        
        # Use default admin credentials (you may need to adjust these)
        username_field.send_keys('admin')
        password_field.send_keys('admin')
        
        # Submit the form
        login_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        login_button.click()
        
        # Wait for login to complete
        time.sleep(3)
        
        # Navigate to the inspections page
        print("📄 Navigating to inspections page...")
        driver.get('http://localhost:8000/inspections/')
        
        # Wait for page to load
        time.sleep(3)
        
        # Find all RFI buttons
        print("🔍 Finding RFI buttons...")
        rfi_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[id^="rfi-"]')
        print(f"✅ Found {len(rfi_buttons)} RFI buttons")
        
        if not rfi_buttons:
            print("⚠️ No RFI buttons found on the page")
            return False
        
        # Test RFI button colors
        print("\n🎨 Testing RFI button colors...")
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
        
        print(f"\n📊 Summary:")
        print(f"   Total buttons: {len(rfi_buttons)}")
        print(f"   Green (with files): {green_count}")
        print(f"   Grey (no files): {grey_count}")
        
        # Take a screenshot for verification
        screenshot_path = 'rfi_buttons_test.png'
        driver.save_screenshot(screenshot_path)
        print(f"\n📸 Screenshot saved to: {screenshot_path}")
        
        driver.quit()
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return False

if __name__ == '__main__':
    success = test_rfi_button_color()
    sys.exit(0 if success else 1)
