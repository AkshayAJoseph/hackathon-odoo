import pytest
from decimal import Decimal
from billing.services import compute_line

class TestComputeLine:
    def test_line_of_1000_with_18_percent_tax(self):
        # Must-pass test 1
        res = compute_line(
            qty=1,
            unit_price=Decimal("1000.00"),
            discount=Decimal("0.00"),
            tax_rate=Decimal("18.00")
        )
        assert res['net'] == Decimal("1000.00")
        assert res['tax'] == Decimal("180.00")
        assert res['total'] == Decimal("1180.00")

    def test_rounding_of_10_005(self):
        # Must-pass test 2: 10.005 rounds to 10.01 (half-up), never float drift
        # E.g. qty=1, unit_price=10.005 (or rate causing .005 tax, e.g. net 200.10 * 5% = 10.005)
        res = compute_line(
            qty=1,
            unit_price=Decimal("200.10"),
            discount=Decimal("0.00"),
            tax_rate=Decimal("5.00") # 200.10 * 0.05 = 10.005 -> 10.01
        )
        assert res['tax'] == Decimal("10.01")
        assert res['total'] == Decimal("210.11")

    def test_discount_applied_before_tax(self):
        # 10% off 5 seats at 200 each (1000 subtotal, 100 discount, 18% tax)
        # Net = 900.00, Tax = 900 * 18% = 162.00, Total = 1062.00
        res = compute_line(
            qty=5,
            unit_price=Decimal("200.00"),
            discount=Decimal("100.00"),
            tax_rate=Decimal("18.00")
        )
        assert res['net'] == Decimal("900.00")
        assert res['tax'] == Decimal("162.00")
        assert res['total'] == Decimal("1062.00")

    def test_discount_capped_never_negative(self):
        # Fixed discount exceeding the line amount
        res = compute_line(
            qty=1,
            unit_price=Decimal("300.00"),
            discount=Decimal("500.00"),
            tax_rate=Decimal("18.00")
        )
        assert res['net'] == Decimal("0.00")
        assert res['tax'] == Decimal("0.00")
        assert res['total'] == Decimal("0.00")
        assert res['discount'] == Decimal("300.00") # capped
