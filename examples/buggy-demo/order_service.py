from config import DEFAULT_TAX_PERCENT
from pricing import apply_tax


def calculate_order_total(lines: list[dict[str, float | int]]) -> float:
    subtotal = sum(line["unit_price"] * line["quantity"] for line in lines)
    return apply_tax(subtotal, DEFAULT_TAX_PERCENT)
