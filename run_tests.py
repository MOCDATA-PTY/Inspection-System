#!/usr/bin/env python3
"""
Quick test runner for needs_retest functionality
"""

import os
import sys
import subprocess
import argparse

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = ['django', 'requests']
    optional_packages = ['selenium']
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - installed")
        except ImportError:
            missing_required.append(package)
            print(f"❌ {package} - missing")
    
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package} - installed")
        except ImportError:
            missing_optional.append(package)
            print(f"⚠️ {package} - missing (optional for comprehensive tests)")
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        print("Install with: pip install " + " ".join(missing_required))
        return False
    
    if missing_optional:
        print(f"\n⚠️ Missing optional packages: {', '.join(missing_optional)}")
        print("Install with: pip install " + " ".join(missing_optional))
        print("These are needed for comprehensive browser testing")
    
    return True

def run_simple_tests():
    """Run simple tests without Selenium"""
    print("\n🚀 Running Simple Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, 'test_needs_retest_simple.py'], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running simple tests: {e}")
        return False

def run_comprehensive_tests():
    """Run comprehensive tests with Selenium"""
    print("\n🚀 Running Comprehensive Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, 'test_needs_retest_comprehensive.py'], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running comprehensive tests: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Run needs_retest functionality tests')
    parser.add_argument('--type', choices=['simple', 'comprehensive', 'both'], 
                       default='simple', help='Type of tests to run')
    parser.add_argument('--check-deps', action='store_true', 
                       help='Only check dependencies')
    
    args = parser.parse_args()
    
    print("🔧 Needs Retest Test Runner")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    if args.check_deps:
        print("\n✅ Dependency check complete")
        return
    
    success = True
    
    if args.type in ['simple', 'both']:
        success &= run_simple_tests()
    
    if args.type in ['comprehensive', 'both']:
        success &= run_comprehensive_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
