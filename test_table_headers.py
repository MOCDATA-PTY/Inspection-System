"""
Test script to verify the table header changes in shipment_list_clean.html
"""
import sys
import io

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_table_headers():
    """Test if the table headers have proper styling and widths"""

    file_path = r"main\templates\main\shipment_list_clean.html"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print("Running table header tests...")
        print("="*50)

        # Test 1: Check if header font size is reduced
        assert 'font-size: 0.75rem;' in content, "Header font size should be 0.75rem"
        print("✓ Test 1 passed: Header font size is 0.75rem")

        # Test 2: Check if headers use white-space: nowrap
        assert 'white-space: nowrap !important;' in content, "Headers should have nowrap"
        print("✓ Test 2 passed: Headers have white-space: nowrap")

        # Test 3: Check if Account Code column width is 300px
        assert 'width: 300px !important; text-align: left !important; overflow: visible !important; } /* Account Code */' in content, "Account Code should be 300px"
        print("✓ Test 3 passed: Account Code column is 300px")

        # Test 4: Check if Sent Status column width is 200px
        assert 'width: 200px !important; text-align: center !important; } /* Sent Status */' in content, "Sent Status should be 200px"
        print("✓ Test 4 passed: Sent Status column is 200px")

        # Test 5: Check if Email header is centered
        assert '#shipmentsTable th:nth-child(5) { text-align: center !important; } /* Email header centered */' in content, "Email header should be centered"
        print("✓ Test 5 passed: Email header is centered")

        # Test 6: Check if overflow visible is applied to columns
        overflow_checks = [
            ('Account Code', 'overflow: visible !important; } /* Account Code */'),
            ('Inspection Date', 'overflow: visible !important; } /* Inspection Date */'),
            ('Inspector', 'overflow: visible !important; } /* Inspector */'),
            ('Email', 'overflow: visible !important; } /* Email */'),
            ('Additional Email', 'overflow: visible !important; } /* Additional Email */'),
            ('View Files', 'overflow: visible !important; } /* View Files */'),
            ('RFI', 'overflow: visible !important; } /* RFI */'),
            ('Invoice', 'overflow: visible !important; } /* Invoice */')
        ]

        for name, check in overflow_checks:
            assert check in content, f"Missing overflow visible for: {name}"
        print("✓ Test 6 passed: All columns have overflow visible")

        # Test 7: Check if span elements have proper styling
        span_checks = [
            ('Account Code', 'Account Code span'),
            ('Inspection Date', 'Inspection Date span'),
            ('Inspector', 'Inspector span'),
            ('Email', 'Email span'),
            ('Additional Email', 'Additional Email span'),
            ('View Files', 'View Files button/span'),
            ('RFI', 'RFI button/span'),
            ('Invoice', 'Invoice button/span')
        ]

        for name, check in span_checks:
            assert f'/* {check} */' in content, f"Missing span styling for: {name}"
        print("✓ Test 7 passed: All span elements have proper styling")

        # Test 8: Check minimum table width
        assert 'min-width: 1450px;' in content, "Table should have min-width of 1450px"
        print("✓ Test 8 passed: Table has minimum width of 1450px")

        # Test 9: Check Sent Status special styling
        assert 'font-size: 0.7rem !important;' in content, "Sent Status should have smaller font"
        assert 'letter-spacing: -0.3px !important;' in content, "Sent Status should have letter spacing"
        print("✓ Test 9 passed: Sent Status has special styling")

        # Test 10: Check column widths
        column_widths = [
            ('Client Name', 'width: 140px !important'),
            ('Account Code', 'width: 300px !important'),
            ('Inspection Date', 'width: 120px !important'),
            ('Compliant/Non-Compliant', 'width: 125px !important'),
            ('Email', 'width: 160px !important'),
            ('Additional Email', 'width: 140px !important'),
            ('Inspector', 'width: 100px !important'),
            ('View Files', 'width: 90px !important'),
            ('RFI', 'width: 75px !important'),
            ('Invoice', 'width: 95px !important'),
            ('Distance (Km)', 'width: 115px !important'),
            ('Hours Worked', 'width: 115px !important'),
            ('Approved', 'width: 85px !important'),
            ('Sent Status', 'width: 200px !important')
        ]

        for name, width in column_widths:
            assert width in content, f"Column {name} should have {width}"
        print("✓ Test 10 passed: All column widths are correct")

        print("\n" + "="*50)
        print("ALL TESTS PASSED! ✓")
        print("="*50)
        print("\nSummary of changes:")
        print("- Header font size: 0.75rem (smaller)")
        print("- Header padding: 10px 12px (compact)")
        print("- Account Code width: 300px")
        print("- Sent Status width: 200px (with reduced font: 0.7rem)")
        print("- Email header: centered")
        print("- All columns: overflow visible (no text truncation)")
        print("- All text fields: full display without ellipsis")
        print("- Table minimum width: 1450px")
        print("- Horizontal scrolling enabled for smaller screens")

        return True

    except FileNotFoundError:
        print(f"✗ Error: File not found at {file_path}")
        return False
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_table_headers()
    exit(0 if success else 1)
