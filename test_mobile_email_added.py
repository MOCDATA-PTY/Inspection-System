#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification test for mobile email input addition
"""
import os
import sys
import re

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("\n" + "="*80)
print("MOBILE EMAIL INPUT - VERIFICATION TEST")
print("="*80)
print("\nVerifying that additional email input was added to mobile view\n")

template_path = os.path.join(
    os.path.dirname(__file__),
    'main', 'templates', 'main', 'shipment_list_clean.html'
)

if not os.path.exists(template_path):
    print("✗ Template not found")
    sys.exit(1)

print("✓ Template found")

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check for the new mobile email section
checks = {
    'Additional Email label in detail view': r'Additional Email.*Mobile Input',
    'Email input in mobile detail': r'additional-emails-container.*fallback_group_id',
    'Email input with type=email': r'type=["\']email["\'].*group-additional-email-input',
    '+ Add Email button in detail': r'\+ Add Email.*addEmailInput',
    'Mobile-friendly min-height': r'min-height:\s*44px',
    'Mobile-friendly font-size': r'font-size:\s*16px',
    'Auto-save onchange': r'onchange=["\']updateGroupAdditionalEmails',
    'Auto-save onblur': r'onblur=["\']updateGroupAdditionalEmails',
    'Email placeholder': r'placeholder=["\']email@example\.com["\']',
}

print("\n" + "="*80)
print("CHECKING MOBILE EMAIL FEATURES")
print("="*80 + "\n")

passed = 0
failed = 0

for check_name, pattern in checks.items():
    if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
        print(f"✓ {check_name}")
        passed += 1
    else:
        print(f"✗ {check_name}")
        failed += 1

print("\n" + "="*80)
print("RESULT")
print("="*80)

print(f"\nPassed: {passed}/{len(checks)}")
print(f"Failed: {failed}/{len(checks)}")

if failed == 0:
    print("\n✓✓✓ ALL CHECKS PASSED!")
    print("\nThe additional email input has been successfully added to mobile view!")
    print("\nFeatures added:")
    print("  ✓ 'Additional Email' input field in mobile detail view")
    print("  ✓ type='email' triggers mobile email keyboard")
    print("  ✓ min-height: 44px (touch-friendly)")
    print("  ✓ font-size: 16px (prevents iOS zoom)")
    print("  ✓ '+ Add Email' button to add multiple emails")
    print("  ✓ Auto-save on change and blur")
    print("  ✓ Proper data-group-id for backend updates")

    print("\n" + "="*80)
    print("HOW TO TEST ON MOBILE")
    print("="*80)
    print("""
1. Open your app on mobile browser
2. Go to Inspections page
3. Tap on any inspection row to expand details
4. Scroll down to see 'Additional Email' section
5. Tap the email input field
6. Email keyboard should appear (with @ key)
7. Type an email and tap outside
8. Email should auto-save
9. Tap '+ Add Email' to add more emails

Expected Result:
  ✓ 'Additional Email' section visible in expanded view
  ✓ Email keyboard appears when tapping input
  ✓ Input is large enough (44px) for easy tapping
  ✓ Auto-saves when tapping outside
  ✓ '+ Add Email' button adds new input fields
    """)
else:
    print(f"\n✗ {failed} checks failed")
    print("\nPlease review the failed checks above")

print("\n" + "="*80)
print("LOCATION IN TEMPLATE")
print("="*80)
print("""
The additional email input was added at approximately line 6535-6558

Section: Mobile Detail View (Expandable Details)
Location: After existing Email display, before Other Details
Parent: <div class="group-details"> (the mobile expandable section)

HTML Structure:
  <div class="mt-4">
    <label>Additional Email</label>
    <div class="additional-emails-container" data-group-id="...">
      <div class="email-inputs">
        <input type="email"
               class="group-additional-email-input"
               placeholder="email@example.com"
               onchange="updateGroupAdditionalEmails(this)"
               style="min-height: 44px; font-size: 16px;">
      </div>
      <button onclick="addEmailInput(this)">+ Add Email</button>
    </div>
  </div>
""")

print("="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
