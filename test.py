#!/usr/bin/env python3
"""
Test script to verify commodity detection logic for Composition button visibility
"""

# Sample inspection data
inspections = [
    {
        'client_name': 'Foodzone Kakamas',
        'account_code': 'RE-IND-PMP-NA-4707',
        'date': '31/10/2025',
        'products': [
            {'inspection_no': '9619', 'commodity': 'RAW', 'product_name': 'single mince'},
            {'inspection_no': '9620', 'commodity': 'RAW', 'product_name': 'wilgenhof boerewors'},
            {'inspection_no': '9621', 'commodity': 'RAW', 'product_name': 'mumbai chilli sausage'},
            {'inspection_no': '9622', 'commodity': 'RAW', 'product_name': 'Biltong flaboured kaas wors'},
        ]
    },
    {
        'client_name': 'Test Client Mixed',
        'account_code': 'RE-IND-MIXED-123',
        'date': '31/10/2025',
        'products': [
            {'inspection_no': '1001', 'commodity': 'RAW', 'product_name': 'raw sausage'},
            {'inspection_no': '1002', 'commodity': 'PMP', 'product_name': 'processed ham'},
            {'inspection_no': '1003', 'commodity': 'RAW', 'product_name': 'raw mince'},
        ]
    },
    {
        'client_name': 'Test Client PMP Only',
        'account_code': 'RE-IND-PMP-456',
        'date': '31/10/2025',
        'products': [
            {'inspection_no': '2001', 'commodity': 'PMP', 'product_name': 'salami'},
            {'inspection_no': '2002', 'commodity': 'PMP', 'product_name': 'bacon'},
        ]
    },
]


def check_composition_button_visibility(inspection):
    """
    Check if Composition button should be visible based on commodities

    Logic: Show button if inspection has RAW OR PMP (or both)
    """
    has_raw = False
    has_pmp = False

    for product in inspection['products']:
        commodity = product['commodity'].upper().strip()

        if commodity == 'RAW':
            has_raw = True
        elif commodity == 'PMP':
            has_pmp = True

    # Show button if RAW OR PMP exists (or both)
    show_button = has_raw or has_pmp

    return {
        'has_raw': has_raw,
        'has_pmp': has_pmp,
        'show_composition_button': show_button
    }


def main():
    print("=" * 80)
    print("COMPOSITION BUTTON VISIBILITY TEST")
    print("=" * 80)
    print()

    for inspection in inspections:
        print(f"Inspection: {inspection['client_name']}")
        print(f"   Account Code: {inspection['account_code']}")
        print(f"   Date: {inspection['date']}")
        print(f"   Products: {len(inspection['products'])}")
        print()

        # List all products and their commodities
        print("   Products breakdown:")
        for product in inspection['products']:
            print(f"      - {product['product_name']}: Commodity = {product['commodity']}")
        print()

        # Check visibility
        result = check_composition_button_visibility(inspection)

        print(f"   Analysis:")
        print(f"      Has RAW products: {'[YES]' if result['has_raw'] else '[NO]'}")
        print(f"      Has PMP products: {'[YES]' if result['has_pmp'] else '[NO]'}")
        print()

        if result['show_composition_button']:
            commodities = []
            if result['has_raw']:
                commodities.append('RAW')
            if result['has_pmp']:
                commodities.append('PMP')
            print(f"   >>> COMPOSITION BUTTON: VISIBLE (has {' and '.join(commodities)})")
        else:
            print(f"   >>> COMPOSITION BUTTON: HIDDEN (no RAW or PMP commodities found)")

        print()
        print("-" * 80)
        print()


if __name__ == '__main__':
    main()

    print("\nSUMMARY:")
    print("The Composition button shows when an inspection group contains:")
    print("   * At least one product with commodity = 'RAW'")
    print("   * OR at least one product with commodity = 'PMP'")
    print("   * OR BOTH")
    print()
    print("The button is hidden only if there are NO RAW or PMP commodities.")
