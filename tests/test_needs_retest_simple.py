#!/usr/bin/env python3
"""
Simple Test Script for Needs Retest Functionality
Tests core functionality without requiring Selenium.
"""

import os
import sys
import django
import json
import requests
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from main.models import FoodSafetyAgencyInspection

class SimpleNeedsRetestTest:
    def __init__(self):
        self.client = Client()
        self.test_results = []
        
    def log_test(self, test_name, status, message=""):
        """Log test results"""
        result = {
            'test_name': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"{status_icon} {test_name}: {message}")
        
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
            
            # Login the test user
            self.client.force_login(user)
            
            # Create test inspection with sample taken
            inspection, created = FoodSafetyAgencyInspection.objects.get_or_create(
                remote_id=1001,
                defaults={
                    'client_name': 'Test Client',
                    'date_of_inspection': '2024-01-15',
                    'is_sample_taken': True,
                    'needs_retest': 'NO',
                    'commodity': 'Test Commodity',
                    'product_class': 'A'
                }
            )
            
            # Create test inspection without sample taken
            inspection_no_sample, created = FoodSafetyAgencyInspection.objects.get_or_create(
                remote_id=1002,
                defaults={
                    'client_name': 'Test Client No Sample',
                    'date_of_inspection': '2024-01-15',
                    'is_sample_taken': False,
                    'needs_retest': 'NO',
                    'commodity': 'Test Commodity',
                    'product_class': 'A'
                }
            )
            
            self.log_test("Test Data Creation", "PASS", f"Created test inspections")
            return True
        except Exception as e:
            self.log_test("Test Data Creation", "FAIL", f"Failed to create test data: {str(e)}")
            return False
    
    def test_backend_api_validation(self):
        """Test backend API validation for needs_retest values"""
        print("\n[TEST] Backend API Validation...")
        
        # Test valid values (both cases) - removed pending due to field length limit
        valid_values = ['YES', 'NO', 'yes', 'no', '']
        for value in valid_values:
            try:
                response = self.client.post('/update-needs-retest/', {
                    'inspection_id': '1001',
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
        invalid_values = ['invalid', 'maybe', '123', 'true', 'false', 'xyz']
        for value in invalid_values:
            try:
                response = self.client.post('/update-needs-retest/', {
                    'inspection_id': '1001',
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
    
    def test_case_conversion(self):
        """Test that case conversion works correctly"""
        print("\n[TEST] Case Conversion...")
        
        test_cases = [
            ('yes', 'YES'),
            ('no', 'NO'),
            ('YES', 'YES'),
            ('NO', 'NO'),
            ('', None)
        ]
        
        for input_value, expected_stored in test_cases:
            try:
                response = self.client.post('/update-needs-retest/', {
                    'inspection_id': '1001',
                    'needs_retest': input_value,
                    'csrfmiddlewaretoken': 'test'
                })
                
                if response.status_code == 200:
                    data = json.loads(response.content)
                    if data.get('success'):
                        # Check what was actually stored in database
                        inspection = FoodSafetyAgencyInspection.objects.get(remote_id=1001)
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
        print("\n[TEST] No Sample Taken Scenario...")
        
        try:
            # Test that API call with no sample returns appropriate response
            response = self.client.post('/update-needs-retest/', {
                'inspection_id': '1002',
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
            
            # Verify that needs_retest is still NO in database
            inspection = FoodSafetyAgencyInspection.objects.get(remote_id=1002)
            if inspection.needs_retest == 'NO':
                self.log_test("No Sample - Database Check", "PASS", "Needs retest remains NO in database")
            else:
                self.log_test("No Sample - Database Check", "FAIL", f"Expected NO, got {inspection.needs_retest}")
                
        except Exception as e:
            self.log_test("No Sample Scenario", "FAIL", f"Exception: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n[TEST] Error Handling...")
        
        # Test with non-existent inspection ID
        try:
            response = self.client.post('/update-needs-retest/', {
                'inspection_id': '9999',
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
    
    def test_database_persistence(self):
        """Test that values are properly persisted in database"""
        print("\n[TEST] Database Persistence...")
        
        test_values = ['YES', 'NO']
        
        for value in test_values:
            try:
                # Update needs_retest
                response = self.client.post('/update-needs-retest/', {
                    'inspection_id': '1001',
                    'needs_retest': value,
                    'csrfmiddlewaretoken': 'test'
                })
                
                if response.status_code == 200:
                    data = json.loads(response.content)
                    if data.get('success'):
                        # Check database
                        inspection = FoodSafetyAgencyInspection.objects.get(remote_id=1001)
                        if inspection.needs_retest == value:
                            self.log_test(f"Database Persistence - '{value}'", "PASS", f"Value '{value}' persisted correctly")
                        else:
                            self.log_test(f"Database Persistence - '{value}'", "FAIL", f"Expected '{value}', got '{inspection.needs_retest}'")
                    else:
                        self.log_test(f"Database Persistence - '{value}'", "FAIL", f"API error: {data.get('error')}")
                else:
                    self.log_test(f"Database Persistence - '{value}'", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Database Persistence - '{value}'", "FAIL", f"Exception: {str(e)}")
    
    def test_template_rendering(self):
        """Test that template renders correctly with different values"""
        print("\n[TEST] Template Rendering...")
        
        try:
            # Test shipment list page loads
            response = self.client.get('/inspections/')
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for mobile dropdown options
                if 'value="yes"' in content and 'value="no"' in content:
                    self.log_test("Template - Mobile Options", "PASS", "Mobile dropdown options found")
                else:
                    self.log_test("Template - Mobile Options", "FAIL", "Mobile dropdown options not found")
                
                # Check for desktop dropdown options
                if 'value="YES"' in content and 'value="NO"' in content:
                    self.log_test("Template - Desktop Options", "PASS", "Desktop dropdown options found")
                else:
                    self.log_test("Template - Desktop Options", "FAIL", "Desktop dropdown options not found")
                
                # Check for JavaScript functions
                if 'updateNeedsRetest' in content and 'updateRetestButtonState' in content:
                    self.log_test("Template - JavaScript Functions", "PASS", "Required JavaScript functions found")
                else:
                    self.log_test("Template - JavaScript Functions", "FAIL", "Required JavaScript functions not found")
                
                # Check for CSS classes
                if 'needs-retest-dropdown' in content:
                    self.log_test("Template - CSS Classes", "PASS", "Required CSS classes found")
                else:
                    self.log_test("Template - CSS Classes", "FAIL", "Required CSS classes not found")
                    
            else:
                self.log_test("Template Rendering", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Template Rendering", "FAIL", f"Exception: {str(e)}")
    
    def generate_report(self):
        """Generate test report"""
        print("\n[REPORT] Generating Test Report...")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*60}")
        print(f"SIMPLE NEEDS RETEST TEST REPORT")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} [PASS]")
        print(f"Failed: {failed_tests} [FAIL]")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"{'='*60}")
        
        if failed_tests > 0:
            print("\n[FAIL] FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test_name']}: {result['message']}")
        
        print(f"\n[PASS] PASSED TESTS:")
        for result in self.test_results:
            if result['status'] == 'PASS':
                print(f"  - {result['test_name']}: {result['message']}")
        
        # Save detailed report to file
        report_file = f"needs_retest_simple_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        
        print(f"\n[INFO] Detailed report saved to: {report_file}")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all simple tests"""
        print("[START] Starting Simple Needs Retest Tests...")
        print("=" * 60)
        
        # Setup
        if not self.create_test_data():
            print("[FAIL] Failed to create test data. Exiting.")
            return False
        
        # Run tests
        self.test_backend_api_validation()
        self.test_case_conversion()
        self.test_no_sample_taken_scenario()
        self.test_error_handling()
        self.test_database_persistence()
        self.test_template_rendering()
        
        # Generate report
        success = self.generate_report()
        
        if success:
            print("\n[SUCCESS] ALL TESTS PASSED! Core needs retest functionality is working correctly.")
        else:
            print("\n[WARNING] SOME TESTS FAILED! Please review the failed tests and fix the issues.")
        
        return success

def main():
    """Main function to run the simple test suite"""
    print("[INFO] Needs Retest Simple Test Suite")
    print("Testing core functionality without Selenium")
    print("=" * 60)
    
    # Run tests
    tester = SimpleNeedsRetestTest()
    success = tester.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
