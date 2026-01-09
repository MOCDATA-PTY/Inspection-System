#!/usr/bin/env python3
"""
Comprehensive Test Script for Needs Retest Functionality
Tests both mobile and desktop views to ensure all actions work correctly.
"""

import os
import sys
import django
import json
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from main.models import FoodSafetyAgencyInspection

class NeedsRetestComprehensiveTest:
    def __init__(self):
        self.client = Client()
        self.test_results = []
        self.base_url = "http://localhost:8000"
        self.driver = None
        
    def log_test(self, test_name, status, message=""):
        """Log test results"""
        result = {
            'test_name': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {message}")
        
    def setup_selenium(self, mobile=False):
        """Setup Selenium WebDriver for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        if mobile:
            # Mobile viewport
            chrome_options.add_argument("--window-size=375,667")
            chrome_options.add_experimental_option("mobileEmulation", {
                "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 2.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
            })
        else:
            # Desktop viewport
            chrome_options.add_argument("--window-size=1920,1080")
            
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            self.log_test("Selenium Setup", "FAIL", f"Failed to setup WebDriver: {str(e)}")
            return False
    
    def teardown_selenium(self):
        """Clean up Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def create_test_data(self):
        """Create test inspection data"""
        try:
            # Create test user
            user, created = User.objects.get_or_create(
                username='testuser',
                defaults={'email': 'test@example.com', 'is_staff': True}
            )
            if created:
                user.set_password('testpass123')
                user.save()
            
            # Create test inspection
            inspection, created = FoodSafetyAgencyInspection.objects.get_or_create(
                remote_id='TEST_RETEST_001',
                defaults={
                    'client_name': 'Test Client',
                    'date_of_inspection': '2024-01-15',
                    'is_sample_taken': True,
                    'needs_retest': 'NO',
                    'commodity': 'Test Commodity',
                    'product_class': 'A'
                }
            )
            
            self.log_test("Test Data Creation", "PASS", f"Created test inspection: {inspection.remote_id}")
            return inspection
        except Exception as e:
            self.log_test("Test Data Creation", "FAIL", f"Failed to create test data: {str(e)}")
            return None
    
    def test_backend_api_validation(self):
        """Test backend API validation for needs_retest values"""
        print("\n🔧 Testing Backend API Validation...")
        
        # Test valid values
        valid_values = ['YES', 'NO', 'yes', 'no', 'pending', 'PENDING', '']
        for value in valid_values:
            try:
                response = self.client.post('/update-needs-retest/', {
                    'inspection_id': 'TEST_RETEST_001',
                    'needs_retest': value,
                    'csrfmiddlewaretoken': 'test'
                })
                
                if response.status_code == 200:
                    data = json.loads(response.content)
                    if data.get('success'):
                        self.log_test(f"Backend API - Valid Value '{value}'", "PASS", "Accepted valid value")
                    else:
                        self.log_test(f"Backend API - Valid Value '{value}'", "FAIL", f"Rejected valid value: {data.get('error')}")
                else:
                    self.log_test(f"Backend API - Valid Value '{value}'", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Backend API - Valid Value '{value}'", "FAIL", f"Exception: {str(e)}")
        
        # Test invalid values
        invalid_values = ['invalid', 'maybe', '123', 'true', 'false']
        for value in invalid_values:
            try:
                response = self.client.post('/update-needs-retest/', {
                    'inspection_id': 'TEST_RETEST_001',
                    'needs_retest': value,
                    'csrfmiddlewaretoken': 'test'
                })
                
                if response.status_code == 200:
                    data = json.loads(response.content)
                    if not data.get('success') and 'Invalid needs_retest value' in data.get('error', ''):
                        self.log_test(f"Backend API - Invalid Value '{value}'", "PASS", "Correctly rejected invalid value")
                    else:
                        self.log_test(f"Backend API - Invalid Value '{value}'", "FAIL", "Should have rejected invalid value")
                else:
                    self.log_test(f"Backend API - Invalid Value '{value}'", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Backend API - Invalid Value '{value}'", "FAIL", f"Exception: {str(e)}")
    
    def test_desktop_view_functionality(self):
        """Test desktop view needs_retest functionality"""
        print("\n🖥️ Testing Desktop View...")
        
        if not self.setup_selenium(mobile=False):
            return
        
        try:
            # Navigate to shipment list
            self.driver.get(f"{self.base_url}/shipment-list/")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "needs-retest-dropdown"))
            )
            
            # Find needs_retest dropdown
            dropdown = self.driver.find_element(By.CLASS_NAME, "needs-retest-dropdown")
            
            # Test dropdown options
            select = Select(dropdown)
            options = [option.get_attribute('value') for option in select.options]
            
            expected_options = ['NO', 'YES']  # Desktop uses uppercase
            if all(opt in options for opt in expected_options):
                self.log_test("Desktop - Dropdown Options", "PASS", f"Found expected options: {options}")
            else:
                self.log_test("Desktop - Dropdown Options", "FAIL", f"Expected {expected_options}, got {options}")
            
            # Test changing value to YES
            select.select_by_value('YES')
            time.sleep(1)  # Wait for AJAX
            
            # Check if retest button is enabled
            try:
                retest_button = self.driver.find_element(By.CSS_SELECTOR, "button[onclick*='uploadRetest']")
                if not retest_button.get_attribute('disabled'):
                    self.log_test("Desktop - Retest Button Enable", "PASS", "Retest button enabled when needs_retest=YES")
                else:
                    self.log_test("Desktop - Retest Button Enable", "FAIL", "Retest button still disabled when needs_retest=YES")
            except NoSuchElementException:
                self.log_test("Desktop - Retest Button Enable", "FAIL", "Retest button not found")
            
            # Test changing value to NO
            select.select_by_value('NO')
            time.sleep(1)  # Wait for AJAX
            
            # Check if retest button is disabled
            try:
                retest_button = self.driver.find_element(By.CSS_SELECTOR, "button[onclick*='uploadRetest']")
                if retest_button.get_attribute('disabled'):
                    self.log_test("Desktop - Retest Button Disable", "PASS", "Retest button disabled when needs_retest=NO")
                else:
                    self.log_test("Desktop - Retest Button Disable", "FAIL", "Retest button still enabled when needs_retest=NO")
            except NoSuchElementException:
                self.log_test("Desktop - Retest Button Disable", "FAIL", "Retest button not found")
                
        except Exception as e:
            self.log_test("Desktop View Test", "FAIL", f"Exception: {str(e)}")
        finally:
            self.teardown_selenium()
    
    def test_mobile_view_functionality(self):
        """Test mobile view needs_retest functionality"""
        print("\n📱 Testing Mobile View...")
        
        if not self.setup_selenium(mobile=True):
            return
        
        try:
            # Navigate to shipment list
            self.driver.get(f"{self.base_url}/shipment-list/")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "needs-retest-dropdown"))
            )
            
            # Find needs_retest dropdown (mobile version)
            dropdown = self.driver.find_element(By.CLASS_NAME, "needs-retest-dropdown")
            
            # Test dropdown options
            select = Select(dropdown)
            options = [option.get_attribute('value') for option in select.options]
            
            expected_options = ['', 'yes', 'no', 'pending']  # Mobile uses lowercase
            if all(opt in options for opt in expected_options):
                self.log_test("Mobile - Dropdown Options", "PASS", f"Found expected options: {options}")
            else:
                self.log_test("Mobile - Dropdown Options", "FAIL", f"Expected {expected_options}, got {options}")
            
            # Test changing value to yes
            select.select_by_value('yes')
            time.sleep(1)  # Wait for AJAX
            
            # Check if retest button is enabled
            try:
                retest_button = self.driver.find_element(By.CSS_SELECTOR, "button[onclick*='uploadRetestFile']")
                if not retest_button.get_attribute('disabled'):
                    self.log_test("Mobile - Retest Button Enable", "PASS", "Retest button enabled when needs_retest=yes")
                else:
                    self.log_test("Mobile - Retest Button Enable", "FAIL", "Retest button still disabled when needs_retest=yes")
            except NoSuchElementException:
                self.log_test("Mobile - Retest Button Enable", "FAIL", "Retest button not found")
            
            # Test changing value to no
            select.select_by_value('no')
            time.sleep(1)  # Wait for AJAX
            
            # Check if retest button is disabled
            try:
                retest_button = self.driver.find_element(By.CSS_SELECTOR, "button[onclick*='uploadRetestFile']")
                if retest_button.get_attribute('disabled'):
                    self.log_test("Mobile - Retest Button Disable", "PASS", "Retest button disabled when needs_retest=no")
                else:
                    self.log_test("Mobile - Retest Button Disable", "FAIL", "Retest button still enabled when needs_retest=no")
            except NoSuchElementException:
                self.log_test("Mobile - Retest Button Disable", "FAIL", "Retest button not found")
            
            # Test changing value to pending
            select.select_by_value('pending')
            time.sleep(1)  # Wait for AJAX
            
            # Check if retest button is disabled
            try:
                retest_button = self.driver.find_element(By.CSS_SELECTOR, "button[onclick*='uploadRetestFile']")
                if retest_button.get_attribute('disabled'):
                    self.log_test("Mobile - Retest Button Pending", "PASS", "Retest button disabled when needs_retest=pending")
                else:
                    self.log_test("Mobile - Retest Button Pending", "FAIL", "Retest button still enabled when needs_retest=pending")
            except NoSuchElementException:
                self.log_test("Mobile - Retest Button Pending", "FAIL", "Retest button not found")
                
        except Exception as e:
            self.log_test("Mobile View Test", "FAIL", f"Exception: {str(e)}")
        finally:
            self.teardown_selenium()
    
    def test_case_sensitivity_handling(self):
        """Test that both uppercase and lowercase values work correctly"""
        print("\n🔄 Testing Case Sensitivity Handling...")
        
        # Test case conversion in backend
        test_cases = [
            ('yes', 'YES'),
            ('no', 'NO'),
            ('pending', 'PENDING'),
            ('YES', 'YES'),
            ('NO', 'NO'),
            ('PENDING', 'PENDING')
        ]
        
        for input_value, expected_stored in test_cases:
            try:
                response = self.client.post('/update-needs-retest/', {
                    'inspection_id': 'TEST_RETEST_001',
                    'needs_retest': input_value,
                    'csrfmiddlewaretoken': 'test'
                })
                
                if response.status_code == 200:
                    data = json.loads(response.content)
                    if data.get('success'):
                        # Check what was actually stored in database
                        inspection = FoodSafetyAgencyInspection.objects.get(remote_id='TEST_RETEST_001')
                        if inspection.needs_retest == expected_stored:
                            self.log_test(f"Case Conversion - '{input_value}'", "PASS", f"Converted to '{expected_stored}'")
                        else:
                            self.log_test(f"Case Conversion - '{input_value}'", "FAIL", f"Expected '{expected_stored}', got '{inspection.needs_retest}'")
                    else:
                        self.log_test(f"Case Conversion - '{input_value}'", "FAIL", f"API error: {data.get('error')}")
                else:
                    self.log_test(f"Case Conversion - '{input_value}'", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Case Conversion - '{input_value}'", "FAIL", f"Exception: {str(e)}")
    
    def test_no_sample_taken_scenario(self):
        """Test behavior when no sample is taken"""
        print("\n🚫 Testing No Sample Taken Scenario...")
        
        # Create inspection without sample
        try:
            inspection, created = FoodSafetyAgencyInspection.objects.get_or_create(
                remote_id='TEST_NO_SAMPLE_001',
                defaults={
                    'client_name': 'Test Client No Sample',
                    'date_of_inspection': '2024-01-15',
                    'is_sample_taken': False,
                    'needs_retest': 'NO',
                    'commodity': 'Test Commodity',
                    'product_class': 'A'
                }
            )
            
            # Test that needs_retest is automatically set to NO
            if inspection.needs_retest == 'NO':
                self.log_test("No Sample - Auto Set NO", "PASS", "Needs retest automatically set to NO")
            else:
                self.log_test("No Sample - Auto Set NO", "FAIL", f"Expected NO, got {inspection.needs_retest}")
            
            # Test that API call with no sample returns appropriate response
            response = self.client.post('/update-needs-retest/', {
                'inspection_id': 'TEST_NO_SAMPLE_001',
                'needs_retest': 'YES',
                'csrfmiddlewaretoken': 'test'
            })
            
            if response.status_code == 200:
                data = json.loads(response.content)
                if data.get('success') and 'automatically set to NO' in data.get('message', ''):
                    self.log_test("No Sample - API Response", "PASS", "API correctly handles no sample scenario")
                else:
                    self.log_test("No Sample - API Response", "FAIL", f"Unexpected API response: {data}")
            else:
                self.log_test("No Sample - API Response", "FAIL", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("No Sample Scenario", "FAIL", f"Exception: {str(e)}")
    
    def test_javascript_functions(self):
        """Test JavaScript functions for button state management"""
        print("\n⚡ Testing JavaScript Functions...")
        
        if not self.setup_selenium(mobile=False):
            return
        
        try:
            # Navigate to shipment list
            self.driver.get(f"{self.base_url}/shipment-list/")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "needs-retest-dropdown"))
            )
            
            # Test updateNeedsRetest function
            dropdown = self.driver.find_element(By.CLASS_NAME, "needs-retest-dropdown")
            select = Select(dropdown)
            
            # Test changing to YES
            select.select_by_value('YES')
            time.sleep(2)  # Wait for AJAX and JavaScript execution
            
            # Check if updateRetestButtonState was called correctly
            retest_button = self.driver.find_element(By.CSS_SELECTOR, "button[onclick*='uploadRetest']")
            button_disabled = retest_button.get_attribute('disabled')
            button_opacity = retest_button.value_of_css_property('opacity')
            
            if not button_disabled and button_opacity != '0.5':
                self.log_test("JavaScript - updateRetestButtonState", "PASS", "Button state updated correctly for YES")
            else:
                self.log_test("JavaScript - updateRetestButtonState", "FAIL", f"Button disabled: {button_disabled}, opacity: {button_opacity}")
            
            # Test changing to NO
            select.select_by_value('NO')
            time.sleep(2)  # Wait for AJAX and JavaScript execution
            
            button_disabled = retest_button.get_attribute('disabled')
            button_opacity = retest_button.value_of_css_property('opacity')
            
            if button_disabled and button_opacity == '0.5':
                self.log_test("JavaScript - updateRetestButtonState", "PASS", "Button state updated correctly for NO")
            else:
                self.log_test("JavaScript - updateRetestButtonState", "FAIL", f"Button disabled: {button_disabled}, opacity: {button_opacity}")
                
        except Exception as e:
            self.log_test("JavaScript Functions Test", "FAIL", f"Exception: {str(e)}")
        finally:
            self.teardown_selenium()
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n⚠️ Testing Error Handling...")
        
        # Test with non-existent inspection ID
        try:
            response = self.client.post('/update-needs-retest/', {
                'inspection_id': 'NON_EXISTENT_001',
                'needs_retest': 'YES',
                'csrfmiddlewaretoken': 'test'
            })
            
            if response.status_code == 200:
                data = json.loads(response.content)
                if not data.get('success') and 'not found' in data.get('error', ''):
                    self.log_test("Error Handling - Non-existent ID", "PASS", "Correctly handled non-existent inspection")
                else:
                    self.log_test("Error Handling - Non-existent ID", "FAIL", f"Unexpected response: {data}")
            else:
                self.log_test("Error Handling - Non-existent ID", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Non-existent ID", "FAIL", f"Exception: {str(e)}")
        
        # Test with invalid method
        try:
            response = self.client.get('/update-needs-retest/')
            
            if response.status_code == 200:
                data = json.loads(response.content)
                if not data.get('success') and 'Invalid request method' in data.get('error', ''):
                    self.log_test("Error Handling - Invalid Method", "PASS", "Correctly handled invalid request method")
                else:
                    self.log_test("Error Handling - Invalid Method", "FAIL", f"Unexpected response: {data}")
            else:
                self.log_test("Error Handling - Invalid Method", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Method", "FAIL", f"Exception: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Generating Test Report...")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*60}")
        print(f"COMPREHENSIVE NEEDS RETEST TEST REPORT")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"{'='*60}")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  • {result['test_name']}: {result['message']}")
        
        print(f"\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['status'] == 'PASS':
                print(f"  • {result['test_name']}: {result['message']}")
        
        # Save detailed report to file
        report_file = f"needs_retest_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'success_rate': (passed_tests/total_tests)*100
                },
                'test_results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Needs Retest Tests...")
        print("=" * 60)
        
        # Setup
        self.create_test_data()
        
        # Run tests
        self.test_backend_api_validation()
        self.test_desktop_view_functionality()
        self.test_mobile_view_functionality()
        self.test_case_sensitivity_handling()
        self.test_no_sample_taken_scenario()
        self.test_javascript_functions()
        self.test_error_handling()
        
        # Generate report
        success = self.generate_report()
        
        if success:
            print("\n🎉 ALL TESTS PASSED! Needs retest functionality is working correctly on both mobile and desktop.")
        else:
            print("\n⚠️ SOME TESTS FAILED! Please review the failed tests and fix the issues.")
        
        return success

def main():
    """Main function to run the comprehensive test suite"""
    print("🔧 Needs Retest Comprehensive Test Suite")
    print("Testing both mobile and desktop functionality")
    print("=" * 60)
    
    # Check if required packages are installed
    try:
        import selenium
        print("✅ Selenium found")
    except ImportError:
        print("❌ Selenium not found. Please install: pip install selenium")
        return False
    
    try:
        import requests
        print("✅ Requests found")
    except ImportError:
        print("❌ Requests not found. Please install: pip install requests")
        return False
    
    # Run tests
    tester = NeedsRetestComprehensiveTest()
    success = tester.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
