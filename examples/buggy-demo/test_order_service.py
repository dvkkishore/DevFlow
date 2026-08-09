import unittest

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
