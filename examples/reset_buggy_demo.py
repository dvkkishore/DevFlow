from pathlib import Path


BUGGY_FILES = {
    "config.py": "DEFAULT_TAX_PERCENT = 20\n",
    "pricing.py": '''def apply_tax(subtotal: float, tax_rate: float) -> float:
    """Apply a decimal tax rate, such as 0.20 for twenty percent."""
    return round(subtotal * (1 + tax_rate), 2)
''',
    "order_service.py": """from config import DEFAULT_TAX_PERCENT
from pricing import apply_tax


def calculate_order_total(lines: list[dict[str, float | int]]) -> float:
    subtotal = sum(line["unit_price"] * line["quantity"] for line in lines)
    return apply_tax(subtotal, DEFAULT_TAX_PERCENT)
""",
    "test_order_service.py": '''import unittest

from order_service import calculate_order_total


class OrderServiceTests(unittest.TestCase):
    def test_applies_configured_tax_percentage(self) -> None:
        lines = [
            {"unit_price": 10.0, "quantity": 2},
            {"unit_price": 5.0, "quantity": 1},
        ]

        self.assertEqual(calculate_order_total(lines), 30.0)

    def test_empty_order_remains_zero(self) -> None:
        self.assertEqual(calculate_order_total([]), 0.0)


if __name__ == "__main__":
    unittest.main()
''',
}


def main() -> None:
    demo_directory = Path(__file__).resolve().parent / "buggy-demo"
    for relative_path, content in BUGGY_FILES.items():
        (demo_directory / relative_path).write_text(content, encoding="utf-8")
    print(f"Restored buggy demo state: {demo_directory}")


if __name__ == "__main__":
    main()
