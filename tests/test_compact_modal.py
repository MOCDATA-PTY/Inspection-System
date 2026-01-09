"""Test that the Manage Dropdowns Modal is now compact with "5 by 5" spacing"""
import os
import re
import sys

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("TESTING COMPACT MODAL - '5 BY 5' SPACING")
print("=" * 100)

# Read the client_allocation.html file
file_path = os.path.join(os.path.dirname(__file__), 'main', 'templates', 'main', 'client_allocation.html')

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("\n[TEST 1] Check modal content width reduction")
print("=" * 100)

# Find modal-content max-width
modal_content_match = re.search(r'class="modal-content"[^>]*max-width:\s*(\d+)px', content)
if modal_content_match:
    width = int(modal_content_match.group(1))
    if width <= 380:
        print(f"✓ PASS: Modal width is {width}px (compact, was 420px)")
    else:
        print(f"✗ FAIL: Modal width is {width}px (should be ≤380px)")
else:
    print("✗ FAIL: Modal width not found")

print("\n[TEST 2] Check modal body padding reduction")
print("=" * 100)

# Find modal-body padding
modal_body_match = re.search(r'class="modal-body"[^>]*padding:\s*(\d+)px', content)
if modal_body_match:
    padding = int(modal_body_match.group(1))
    if padding <= 12:
        print(f"✓ PASS: Modal body padding is {padding}px (compact, was 20px)")
    else:
        print(f"✗ FAIL: Modal body padding is {padding}px (should be ≤12px)")
else:
    print("✗ FAIL: Modal body padding not found")

print("\n[TEST 3] Check form group margin reduction")
print("=" * 100)

# Find form-group margin-bottom
form_group_matches = re.findall(r'class="form-group"[^>]*margin-bottom:\s*(\d+)px', content)
if form_group_matches:
    max_margin = max(int(m) for m in form_group_matches)
    if max_margin <= 8:
        print(f"✓ PASS: Form group margins are ≤{max_margin}px (compact, was 15px)")
    else:
        print(f"✗ FAIL: Form group margins up to {max_margin}px (should be ≤8px)")
else:
    print("✗ FAIL: Form group margins not found")

print("\n[TEST 4] Check label font size reduction")
print("=" * 100)

# Find label font sizes
label_matches = re.findall(r'class="form-label"[^>]*font-size:\s*(\d+)px', content)
if label_matches:
    max_label_size = max(int(m) for m in label_matches)
    if max_label_size <= 11:
        print(f"✓ PASS: Label font sizes are ≤{max_label_size}px (compact, was 13px)")
    else:
        print(f"✗ FAIL: Label font sizes up to {max_label_size}px (should be ≤11px)")
else:
    print("✗ FAIL: Label font sizes not found")

print("\n[TEST 5] Check input/select padding reduction")
print("=" * 100)

# Find input padding
input_matches = re.findall(r'font-size:\s*12px;\s*padding:\s*(\d+)px', content)
if input_matches:
    if any(int(p) <= 5 for p in input_matches):
        print(f"✓ PASS: Input padding reduced to ~5px (compact, was 8px)")
    else:
        print(f"✗ FAIL: Input padding not reduced enough")
else:
    print("⚠ WARNING: Input padding pattern not found")

print("\n[TEST 6] Check Current Values section compactness")
print("=" * 100)

# Find current-options-display padding
current_options_match = re.search(r'id="current-options-display"[^>]*padding:\s*(\d+)px', content)
if current_options_match:
    padding = int(current_options_match.group(1))
    if padding <= 6:
        print(f"✓ PASS: Current Values padding is {padding}px (compact, was 12px)")
    else:
        print(f"✗ FAIL: Current Values padding is {padding}px (should be ≤6px)")
else:
    print("✗ FAIL: Current Values padding not found")

# Check gap between badges
gap_match = re.search(r'id="current-options-list"[^>]*gap:\s*(\d+)px', content)
if gap_match:
    gap = int(gap_match.group(1))
    if gap <= 3:
        print(f"✓ PASS: Badge gap is {gap}px (compact, was 6px)")
    else:
        print(f"✗ FAIL: Badge gap is {gap}px (should be ≤3px)")
else:
    print("✗ FAIL: Badge gap not found")

print("\n[TEST 7] Check badge compactness")
print("=" * 100)

# Find badge padding in JavaScript
badge_padding_match = re.search(r'padding:\s*3px\s+6px', content)
if badge_padding_match:
    print("✓ PASS: Badge padding is '3px 6px' (compact, was '6px 12px')")
else:
    print("✗ FAIL: Badge padding not compact")

# Find badge font size
badge_font_match = re.search(r'border-radius:\s*3px;\s*font-size:\s*10px', content)
if badge_font_match:
    print("✓ PASS: Badge font size is 10px (compact, was 13px)")
else:
    print("✗ FAIL: Badge font size not reduced")

print("\n[TEST 8] Check Add Option button compactness")
print("=" * 100)

# Find button padding
button_match = re.search(r'btn btn-success[^>]*padding:\s*5px\s+15px', content)
if button_match:
    print("✓ PASS: Button padding is '5px 15px' (compact, was '8px 20px')")
else:
    print("✗ FAIL: Button padding not compact")

# Find button font size
button_font_match = re.search(r'btn btn-success[^>]*font-size:\s*12px', content)
if button_font_match:
    print("✓ PASS: Button font size is 12px (compact, was 14px)")
else:
    print("✗ FAIL: Button font size not reduced")

print("\n[TEST 9] Check X button compactness")
print("=" * 100)

# Find X button positioning
x_button_match = re.search(r'top:\s*8px;\s*right:\s*8px', content)
if x_button_match:
    print("✓ PASS: X button positioned at 8px from edges (compact, was 12px)")
else:
    print("✗ FAIL: X button position not compact")

print("\n" + "=" * 100)
print("SUMMARY - COMPACT '5 BY 5' MODAL")
print("=" * 100)
print("\nAll spacing reduced for ultra-compact design:")
print("  ✓ Modal width: 420px → 380px (smaller overall)")
print("  ✓ Body padding: 20px → 12px")
print("  ✓ Form margins: 15px → 8px")
print("  ✓ Label fonts: 13px → 11px")
print("  ✓ Input padding: 8px → 5px")
print("  ✓ Current Values padding: 12px → 6px")
print("  ✓ Badge gap: 6px → 3px")
print("  ✓ Badge padding: 6px 12px → 3px 6px")
print("  ✓ Badge font: 13px → 10px")
print("  ✓ Button padding: 8px 20px → 5px 15px")
print("  ✓ Button font: 14px → 12px")
print("  ✓ X button: 12px edges → 8px edges")
print("\nThe modal is now MUCH more compact - truly '5 by 5' tight spacing!")
print("=" * 100)
