# Buggy Order Demo

This small application calculates an order total using the configured sales-tax percentage.

Run the tests with:

```powershell
python -m unittest -v
```

For an order with a subtotal of `25.00` and `DEFAULT_TAX_PERCENT = 20`, the final total should be `30.00`.
