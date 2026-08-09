def apply_tax(subtotal: float, tax_rate: float) -> float:
    """Apply a decimal tax rate, such as 0.20 for twenty percent."""
    return round(subtotal * (1 + tax_rate), 2)
