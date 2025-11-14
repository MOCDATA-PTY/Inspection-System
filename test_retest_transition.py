#!/usr/bin/env python3
"""
Test script to measure retest button transition performance
"""

import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

def test_retest_button_transition():
    """Test how long it takes for retest button to transition from disabled to enabled"""
    
    print("🧪 Starting Retest Button Transition Performance Test")
    print("=" * 60)
    
    # Setup Chrome options for headless testing
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = None
    
    try:
        # Start Chrome driver
        print("🚀 Starting Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        # Navigate to the inspections page
        print("🌐 Navigating to inspections page...")
        base_url = "http://localhost:8000"
        login_url = f"{base_url}/login/"
        inspections_url = f"{base_url}/inspections/"
        
        # Login first (assuming developer credentials)
        driver.get(login_url)
        time.sleep(2)
        
        # Fill login form
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys("developer")
        password_field.send_keys("developer123")  # Adjust password as needed
        
        # Submit login
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        time.sleep(3)
        
        # Navigate to inspections page
        driver.get(inspections_url)
        print("⏳ Waiting for page to load...")
        time.sleep(5)  # Wait for page to fully load
        
        # Find the first expandable group and expand it
        print("🔍 Looking for expandable groups...")
        expand_buttons = driver.find_elements(By.CSS_SELECTOR, ".expand-btn")
        
        if not expand_buttons:
            print("❌ No expand buttons found!")
            return
            
        print(f"✅ Found {len(expand_buttons)} expand buttons")
        
        # Click the first expand button
        expand_buttons[0].click()
        time.sleep(2)
        
        # Find a retest dropdown that's not disabled
        print("🔍 Looking for enabled retest dropdowns...")
        retest_dropdowns = driver.find_elements(By.CSS_SELECTOR, ".needs-retest-dropdown:not([disabled])")
        
        if not retest_dropdowns:
            print("❌ No enabled retest dropdowns found!")
            return
            
        print(f"✅ Found {len(retest_dropdowns)} enabled retest dropdowns")
        
        # Test the first available dropdown
        dropdown = retest_dropdowns[0]
        inspection_id = dropdown.get_attribute("data-inspection-id")
        print(f"🎯 Testing dropdown for inspection ID: {inspection_id}")
        
        # Find the corresponding retest button
        retest_button = driver.find_element(By.ID, f"retest-{inspection_id}")
        
        if not retest_button:
            print(f"❌ Retest button not found for inspection {inspection_id}")
            return
            
        print("✅ Found retest button")
        
        # Test 1: Measure time from dropdown change to button enabled
        print("\n🧪 TEST 1: Dropdown 'No' → 'Yes' (Button Disabled → Enabled)")
        print("-" * 50)
        
        # Set dropdown to 'NO' first
        dropdown_select = Select(dropdown)
        dropdown_select.select_by_value("NO")
        time.sleep(1)
        
        # Check initial button state
        initial_disabled = retest_button.get_attribute("disabled")
        print(f"📊 Initial button disabled state: {initial_disabled}")
        
        # Measure transition time
        start_time = time.time()
        
        # Change dropdown to 'YES'
        dropdown_select.select_by_value("YES")
        
        # Wait for button to become enabled and measure time
        wait_time = 0
        max_wait = 5.0  # Maximum 5 seconds
        check_interval = 0.01  # Check every 10ms
        
        while wait_time < max_wait:
            current_disabled = retest_button.get_attribute("disabled")
            current_opacity = retest_button.value_of_css_property("opacity")
            current_cursor = retest_button.value_of_css_property("cursor")
            
            # Check if button is now enabled (not disabled and opacity = 1)
            if not current_disabled and current_opacity == "1":
                end_time = time.time()
                transition_time = (end_time - start_time) * 1000  # Convert to milliseconds
                print(f"✅ Button enabled after: {transition_time:.2f}ms")
                print(f"📊 Final button state: disabled={current_disabled}, opacity={current_opacity}, cursor={current_cursor}")
                break
                
            time.sleep(check_interval)
            wait_time += check_interval
        else:
            print(f"❌ Button did not enable within {max_wait} seconds")
            
        # Test 2: Measure time from 'Yes' to 'No' (Button Enabled → Disabled)
        print("\n🧪 TEST 2: Dropdown 'Yes' → 'No' (Button Enabled → Disabled)")
        print("-" * 50)
        
        time.sleep(1)  # Brief pause
        start_time = time.time()
        
        # Change dropdown back to 'NO'
        dropdown_select.select_by_value("NO")
        
        # Wait for button to become disabled
        wait_time = 0
        while wait_time < max_wait:
            current_disabled = retest_button.get_attribute("disabled")
            current_opacity = retest_button.value_of_css_property("opacity")
            
            # Check if button is now disabled
            if current_disabled or current_opacity == "0.5":
                end_time = time.time()
                transition_time = (end_time - start_time) * 1000
                print(f"✅ Button disabled after: {transition_time:.2f}ms")
                print(f"📊 Final button state: disabled={current_disabled}, opacity={current_opacity}")
                break
                
            time.sleep(check_interval)
            wait_time += check_interval
        else:
            print(f"❌ Button did not disable within {max_wait} seconds")
            
        # Test 3: Multiple rapid changes
        print("\n🧪 TEST 3: Rapid Toggle Test (5 cycles)")
        print("-" * 50)
        
        total_times = []
        
        for i in range(5):
            print(f"🔄 Cycle {i+1}/5")
            
            # No → Yes
            start_time = time.time()
            dropdown_select.select_by_value("YES")
            
            # Wait for enabled state
            wait_time = 0
            while wait_time < 2.0:  # Shorter max wait for rapid test
                if not retest_button.get_attribute("disabled") and retest_button.value_of_css_property("opacity") == "1":
                    cycle_time = (time.time() - start_time) * 1000
                    total_times.append(cycle_time)
                    print(f"   ✅ Enabled in {cycle_time:.2f}ms")
                    break
                time.sleep(0.005)  # 5ms intervals for rapid testing
                wait_time += 0.005
            
            time.sleep(0.1)  # Brief pause between changes
            
            # Yes → No (for next cycle)
            if i < 4:  # Don't do this on the last cycle
                dropdown_select.select_by_value("NO")
                time.sleep(0.1)
        
        # Calculate statistics
        if total_times:
            avg_time = sum(total_times) / len(total_times)
            min_time = min(total_times)
            max_time = max(total_times)
            
            print(f"\n📊 PERFORMANCE STATISTICS:")
            print(f"   Average transition time: {avg_time:.2f}ms")
            print(f"   Fastest transition: {min_time:.2f}ms")
            print(f"   Slowest transition: {max_time:.2f}ms")
            print(f"   Total cycles completed: {len(total_times)}")
            
            # Performance assessment
            if avg_time < 50:
                print("✅ EXCELLENT: Transition is very fast (< 50ms)")
            elif avg_time < 100:
                print("✅ GOOD: Transition is fast (< 100ms)")
            elif avg_time < 200:
                print("⚠️ MODERATE: Transition is acceptable (< 200ms)")
            elif avg_time < 500:
                print("⚠️ SLOW: Transition is noticeable (< 500ms)")
            else:
                print("❌ VERY SLOW: Transition is too slow (> 500ms)")
        
        print("\n🎯 RECOMMENDATIONS:")
        if avg_time > 100:
            print("   - Remove all CSS transitions from .btn-retest")
            print("   - Ensure JavaScript updates DOM properties directly")
            print("   - Consider using CSS classes instead of inline styles")
        else:
            print("   - Performance is acceptable")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        
    finally:
        if driver:
            print("🧹 Closing browser...")
            driver.quit()
            
    print("\n✅ Test completed!")

def test_network_performance():
    """Test the AJAX call performance for updating retest status"""
    
    print("\n🌐 Testing AJAX Performance")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    update_url = f"{base_url}/update-needs-retest/"
    
    # Test data
    test_data = {
        'inspection_id': '8650',  # Use a real inspection ID from your data
        'needs_retest': 'YES',
        'csrfmiddlewaretoken': 'test'  # This would need to be a real token
    }
    
    print("📡 Testing AJAX call speed...")
    
    try:
        start_time = time.time()
        
        # Note: This would fail without proper authentication and CSRF token
        # But we can measure the connection time
        response = requests.post(update_url, data=test_data, timeout=5)
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        print(f"📊 AJAX Response Time: {response_time:.2f}ms")
        print(f"📊 Status Code: {response.status_code}")
        
        if response_time < 100:
            print("✅ EXCELLENT: AJAX is very fast")
        elif response_time < 300:
            print("✅ GOOD: AJAX is fast")
        else:
            print("⚠️ SLOW: AJAX response is slow")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network test failed: {e}")
        print("💡 This is expected without proper authentication")

if __name__ == "__main__":
    print("🧪 RETEST BUTTON TRANSITION PERFORMANCE TEST")
    print("=" * 60)
    print("📋 This test will measure:")
    print("   1. Time for button to enable when dropdown = 'Yes'")
    print("   2. Time for button to disable when dropdown = 'No'")
    print("   3. Rapid toggle performance")
    print("   4. AJAX call performance")
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        print("✅ Django server is running")
    except:
        print("❌ Django server is not running!")
        print("💡 Please start the server with: python manage.py runserver")
        exit(1)
    
    # Run the main test
    test_retest_button_transition()
    
    # Run network performance test
    test_network_performance()
    
    print("\n🏁 All tests completed!")
