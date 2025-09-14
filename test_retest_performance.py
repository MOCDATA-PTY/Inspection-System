#!/usr/bin/env python3
"""
Simple performance test for retest button transition
Tests the server-side response time for AJAX calls
"""

import time
import requests
import json
import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def test_ajax_performance():
    """Test the AJAX call performance for updating retest status"""
    
    print("🧪 RETEST BUTTON AJAX PERFORMANCE TEST")
    print("=" * 50)
    
    # Create Django test client
    client = Client()
    User = get_user_model()
    
    try:
        # Try to login as developer user
        user = User.objects.filter(username='developer').first()
        if not user:
            print("❌ Developer user not found!")
            return
            
        # Login
        login_success = client.login(username='developer', password='developer123')
        if not login_success:
            print("❌ Failed to login as developer")
            return
            
        print("✅ Logged in as developer")
        
        # Get a real inspection ID from the database
        from main.models import FoodSafetyAgencyInspection
        inspection = FoodSafetyAgencyInspection.objects.filter(is_sample_taken=True).first()
        
        if not inspection:
            print("❌ No sample-taken inspections found!")
            return
            
        inspection_id = inspection.remote_id
        print(f"🎯 Testing with inspection ID: {inspection_id}")
        
        # Test 1: Update to YES
        print("\n🧪 TEST 1: Setting retest to 'YES'")
        start_time = time.time()
        
        response = client.post('/update-needs-retest/', {
            'inspection_id': inspection_id,
            'needs_retest': 'YES'
        })
        
        end_time = time.time()
        response_time_yes = (end_time - start_time) * 1000
        
        print(f"📊 Response time: {response_time_yes:.2f}ms")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📊 Success: {data.get('success', False)}")
            except:
                print("📊 Response is not JSON")
        
        time.sleep(0.1)  # Brief pause
        
        # Test 2: Update to NO
        print("\n🧪 TEST 2: Setting retest to 'NO'")
        start_time = time.time()
        
        response = client.post('/update-needs-retest/', {
            'inspection_id': inspection_id,
            'needs_retest': 'NO'
        })
        
        end_time = time.time()
        response_time_no = (end_time - start_time) * 1000
        
        print(f"📊 Response time: {response_time_no:.2f}ms")
        print(f"📊 Status code: {response.status_code}")
        
        # Test 3: Rapid toggle test
        print("\n🧪 TEST 3: Rapid Toggle Test (10 cycles)")
        times = []
        
        for i in range(10):
            value = 'YES' if i % 2 == 0 else 'NO'
            
            start_time = time.time()
            response = client.post('/update-needs-retest/', {
                'inspection_id': inspection_id,
                'needs_retest': value
            })
            end_time = time.time()
            
            cycle_time = (end_time - start_time) * 1000
            times.append(cycle_time)
            print(f"   Cycle {i+1}: {value} → {cycle_time:.2f}ms")
        
        # Calculate statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📊 AJAX PERFORMANCE STATISTICS:")
        print(f"   Average response time: {avg_time:.2f}ms")
        print(f"   Fastest response: {min_time:.2f}ms")
        print(f"   Slowest response: {max_time:.2f}ms")
        
        # Performance assessment
        if avg_time < 50:
            print("✅ EXCELLENT: Server response is very fast")
        elif avg_time < 100:
            print("✅ GOOD: Server response is fast")
        elif avg_time < 200:
            print("⚠️ MODERATE: Server response is acceptable")
        else:
            print("❌ SLOW: Server response is too slow")
            
    except Exception as e:
        print(f"❌ Error during AJAX testing: {e}")

def analyze_css_transitions():
    """Analyze CSS transitions in the template"""
    
    print("\n🎨 CSS TRANSITION ANALYSIS")
    print("=" * 40)
    
    template_file = "main/templates/main/shipment_list_clean.html"
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for transition properties
        transition_lines = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if 'transition:' in line.lower() and ('btn-retest' in lines[max(0, i-10):i] or 
                                                  'btn-lab' in lines[max(0, i-10):i] or
                                                  'btn-upload' in lines[max(0, i-10):i]):
                transition_lines.append((i, line.strip()))
        
        if transition_lines:
            print("🔍 Found transition properties affecting buttons:")
            for line_num, line in transition_lines:
                print(f"   Line {line_num}: {line}")
        else:
            print("✅ No transition properties found on button classes")
            
        # Check for any remaining transition properties
        all_transitions = []
        for i, line in enumerate(lines, 1):
            if 'transition:' in line.lower():
                all_transitions.append((i, line.strip()))
                
        print(f"\n📊 Total transition properties in template: {len(all_transitions)}")
        
        if len(all_transitions) > 10:
            print("⚠️ Many transitions found - this could affect performance")
            print("💡 Consider removing unnecessary transitions")
        
    except FileNotFoundError:
        print(f"❌ Template file not found: {template_file}")
    except Exception as e:
        print(f"❌ Error analyzing CSS: {e}")

def create_js_performance_test():
    """Create a JavaScript snippet for browser console testing"""
    
    js_test = """
// RETEST BUTTON PERFORMANCE TEST - Paste this in browser console
console.log('🧪 Starting Retest Button Performance Test');

function testRetestButtonTransition() {
    // Find first enabled retest dropdown
    const dropdown = document.querySelector('.needs-retest-dropdown:not([disabled])');
    if (!dropdown) {
        console.log('❌ No enabled retest dropdown found');
        return;
    }
    
    const inspectionId = dropdown.getAttribute('data-inspection-id');
    const retestButton = document.getElementById('retest-' + inspectionId);
    
    if (!retestButton) {
        console.log('❌ Retest button not found');
        return;
    }
    
    console.log('✅ Found dropdown and button for inspection:', inspectionId);
    
    // Test function
    function measureTransition(fromValue, toValue, testName) {
        return new Promise((resolve) => {
            console.log(`\\n🧪 ${testName}: ${fromValue} → ${toValue}`);
            
            // Set initial state
            dropdown.value = fromValue;
            
            // Trigger change to update button state
            const changeEvent = new Event('change', { bubbles: true });
            dropdown.dispatchEvent(changeEvent);
            
            // Wait a moment for initial state
            setTimeout(() => {
                const startTime = performance.now();
                
                // Change to target value
                dropdown.value = toValue;
                dropdown.dispatchEvent(changeEvent);
                
                // Check button state repeatedly until it changes
                function checkState() {
                    const disabled = retestButton.disabled;
                    const opacity = window.getComputedStyle(retestButton).opacity;
                    const cursor = window.getComputedStyle(retestButton).cursor;
                    
                    const expectedDisabled = !(toValue === 'YES');
                    const expectedOpacity = toValue === 'YES' ? '1' : '0.5';
                    
                    if (disabled === expectedDisabled && opacity === expectedOpacity) {
                        const endTime = performance.now();
                        const duration = endTime - startTime;
                        console.log(`   ✅ Transition completed in ${duration.toFixed(2)}ms`);
                        console.log(`   📊 Final state: disabled=${disabled}, opacity=${opacity}, cursor=${cursor}`);
                        resolve(duration);
                    } else {
                        // Check again in next frame
                        requestAnimationFrame(checkState);
                    }
                }
                
                // Start checking immediately
                requestAnimationFrame(checkState);
            }, 100);
        });
    }
    
    // Run tests
    async function runTests() {
        const times = [];
        
        // Test 1: NO → YES (disabled → enabled)
        const time1 = await measureTransition('NO', 'YES', 'Disabled → Enabled');
        times.push(time1);
        
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Test 2: YES → NO (enabled → disabled)
        const time2 = await measureTransition('YES', 'NO', 'Enabled → Disabled');
        times.push(time2);
        
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Test 3: Rapid toggles
        console.log('\\n🧪 TEST 3: Rapid Toggle Test (5 cycles)');
        for (let i = 0; i < 5; i++) {
            const value = i % 2 === 0 ? 'YES' : 'NO';
            const time = await measureTransition(i % 2 === 0 ? 'NO' : 'YES', value, `Rapid ${i+1}`);
            times.push(time);
            await new Promise(resolve => setTimeout(resolve, 50));
        }
        
        // Statistics
        const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
        const minTime = Math.min(...times);
        const maxTime = Math.max(...times);
        
        console.log('\\n📊 PERFORMANCE RESULTS:');
        console.log(`   Average: ${avgTime.toFixed(2)}ms`);
        console.log(`   Fastest: ${minTime.toFixed(2)}ms`);
        console.log(`   Slowest: ${maxTime.toFixed(2)}ms`);
        
        if (avgTime < 16) {
            console.log('✅ EXCELLENT: Transition is instant (< 1 frame)');
        } else if (avgTime < 50) {
            console.log('✅ GOOD: Transition is very fast');
        } else if (avgTime < 100) {
            console.log('⚠️ MODERATE: Transition is noticeable');
        } else {
            console.log('❌ SLOW: Transition is too slow');
        }
    }
    
    runTests().catch(console.error);
}

// Run the test
testRetestButtonTransition();
"""
    
    print("\n📋 JAVASCRIPT CONSOLE TEST")
    print("=" * 40)
    print("Copy and paste this code into your browser console on the inspections page:")
    print("\n" + "="*60)
    print(js_test)
    print("="*60)

if __name__ == "__main__":
    print("🧪 RETEST BUTTON PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    # Test 1: Server-side performance
    test_ajax_performance()
    
    # Test 2: CSS analysis
    analyze_css_transitions()
    
    # Test 3: Browser test instructions
    create_js_performance_test()
    
    print(f"\n🏁 Analysis completed!")
    print("\n💡 RECOMMENDATIONS:")
    print("   1. Run the JavaScript test in your browser console")
    print("   2. Check if any CSS transitions are still affecting buttons")
    print("   3. Ensure AJAX calls are responding quickly")
