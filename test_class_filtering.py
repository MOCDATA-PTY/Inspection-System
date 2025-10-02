import sys


def normalize_label(text: str) -> str:
    s = (text or "").strip().lower()
    # Basic normalization similar to frontend: collapse whitespace
    s = " ".join(s.split())
    return s


RAW_ALLOWED = [
    "Raw Braaiwors / Sizzler",
    "Raw Banger / Griller",
    "Economy Burger/ Econo Burger/ Economy Patty/ Econo Patty/ Budget Burger",
    "Value burger/ Value patty/ Value hamburger/ Value meatball/ Value frikkadel",
    "Burger / Patty / Hamburger Patty / Meatball / Frikkadel = Regular",
    "Burger / Patty / Hamburger Patty / Meatball / Frikkadel = Lean",
    "Burger / Patty / Hamburger Patty / Meatball / Frikkadel = Extra Lean",
    "Ground Burger / Ground patty = Regular",
    "Ground Burger / Ground patty = Lean",
    "Ground Burger / Ground patty = Extra Lean",
    "Raw mixed species sausage / wors",
    "Raw species sausage / wors",
    "Raw Boerewors",
    "Raw Flavoured mixed species Ground Meat & Offal",
    "Raw Flavoured mixed species Ground Meat",
    "Raw Flavoured Ground Meat & Offal",
    "Raw Flavoured Ground Meat",
    "Regular Mince",
    "Lean Mince",
    "Extra Lean Mince",
]

PMP_ALLOWED = [
    "Whole muscle, cured, heat treated products",
    "Whole muscle, dry cured, heat treated products",
    "Whole Muscle, uncured and heat / partial treated products",
    "Whole muscle, uncured, no or partial heat treated and air dried products",
    "Whole muscle, uncured, no or partial heat treated and air dried products undergoing a lengthy maturation period (minimum 21 days)",
    "Whole muscle, dry cured, no or partial heat treated products",
    "Whole muscle, cured and no or partial heat treated products",
    "Whole muscle, cured, no or partial heat treated and air dried products",
    "Whole muscle, dry cured, no or partial heat treated and dried products",
    "Comminuted, cured and heat treated products",
    "Liver spreads, pates and terrines",
    "Products in aspic: Brawn",
    "Product in aspic: Suelze",
    "Other products containing cured meat pieces in aspic",
    "Products made from blood",
    "Comminuted, uncured, no or partial heat treated and dried products",
    "Comminuted, cured, no or partial heat treated, dried and fermented products",
    "Comminuted, uncured and heat treated products",
    "Reformed, uncured and no or partial heat treated products",
    "Reformed, cured, heat treated products from single species",
    "Reformed, cured, heat treated products from mixed species",
    "Reformed, cured and no or partial heat treated products",
    "Coated Processed Meat Products",
    "Unspecified processed meat products",
]


def main() -> int:
    raw_norm = {normalize_label(x) for x in RAW_ALLOWED}
    pmp_norm = {normalize_label(x) for x in PMP_ALLOWED}

    # Ensure RAW and PMP do not accidentally include each other
    overlap = raw_norm.intersection(pmp_norm)
    if overlap:
        print("ERROR: RAW and PMP lists overlap:", sorted(overlap))
        return 1

    # Ensure RAW list does not include Unspecified processed meat products
    if normalize_label("Unspecified processed meat products") in raw_norm:
        print("ERROR: RAW contains 'Unspecified processed meat products', which is not allowed")
        return 1

    # Ensure key samples exist in each list
    must_have_raw = [
        "Raw Boerewors",
        "Regular Mince",
        "Burger / Patty / Hamburger Patty / Meatball / Frikkadel = Regular",
    ]
    for label in must_have_raw:
        if normalize_label(label) not in raw_norm:
            print(f"ERROR: RAW missing required option: {label}")
            return 1

    must_have_pmp = [
        "Comminuted, cured and heat treated products",
        "Whole muscle, cured, heat treated products",
        "Unspecified processed meat products",
    ]
    for label in must_have_pmp:
        if normalize_label(label) not in pmp_norm:
            print(f"ERROR: PMP missing required option: {label}")
            return 1

    print("OK: RAW and PMP class lists are correctly defined and mutually exclusive.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


