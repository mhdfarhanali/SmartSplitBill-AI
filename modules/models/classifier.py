"""
This module automatically tags items into categories
based on simple keyword patterns.

Used by:
- ReceiptData (auto_tag)
- InsightsEngine (category summary)
"""

def auto_tag(name: str) -> str:
    """Simple rule-based category classifier for receipt items."""
    n = name.lower().strip()

    # Food
    if any(k in n for k in ["nasi", "rice", "burger", "mie", "toast", "cake", "bread", "pizza", "soup", "chicken", "udang", "pangsit", "siomay"]):
        return "Food"

    # Beverage
    if any(k in n for k in ["coffee", "latte", "americano", "tea", "milk", "juice", "float", "ice", "korean", "mineral", "mocha"]):
        return "Beverage"

    # Service / Charge
    if any(k in n for k in ["tax", "service", "fee", "charge"]):
        return "Service"

    # Fashion
    if any(k in n for k in ["shirt", "pants", "bag", "shoe", "jacket", "hat", "dress"]):
        return "Fashion"

    # Toiletries
    if any(k in n for k in ["soap", "shampo", "toothpaste", "tissue", "micellar", "cleanser", "toner", "serum", "perfume"]):
        return "Toiletries"

    # Stationery
    if any(k in n for k in ["pen", "book", "notebook", "pencil", "marker", "eraser"]):
        return "Stationery"

    # Default
    return "Others"
