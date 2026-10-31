import pytest
from decimal import Decimal
from catalog.models import Product, Tax
from catalog.services import resolve_tax

@pytest.mark.django_db
class TestResolveTax:
    def test_product_tax_beats_default_tax(self):
        product = Product.objects.create(name="SaaS Pro", sales_price=Decimal("100.00"))
        default_tax = Tax.objects.create(name="Default 18%", rate_percent=Decimal("18.00"), applies_to=None, is_active=True)
        product_tax = Tax.objects.create(name="Special 5%", rate_percent=Decimal("5.00"), applies_to=product, is_active=True)

        class DummyLine:
            def __init__(self, prod):
                self.product = prod

        resolved = resolve_tax(DummyLine(product))
        assert resolved == product_tax
        assert resolved.rate_percent == Decimal("5.00")

    def test_default_tax_used_when_product_has_none(self):
        product = Product.objects.create(name="Addon", sales_price=Decimal("50.00"))
        default_tax = Tax.objects.create(name="Default 18%", rate_percent=Decimal("18.00"), applies_to=None, is_active=True)

        class DummyLine:
            def __init__(self, prod):
                self.product = prod

        resolved = resolve_tax(DummyLine(product))
        assert resolved == default_tax
        assert resolved.rate_percent == Decimal("18.00")

    def test_zero_when_neither(self):
        product = Product.objects.create(name="Basic", sales_price=Decimal("10.00"))

        class DummyLine:
            def __init__(self, prod):
                self.product = prod

        resolved = resolve_tax(DummyLine(product))
        assert resolved is None

    def test_inactive_taxes_ignored(self):
        product = Product.objects.create(name="Consulting", sales_price=Decimal("200.00"))
        Tax.objects.create(name="Old Tax", rate_percent=Decimal("20.00"), applies_to=product, is_active=False)
        Tax.objects.create(name="Old Default", rate_percent=Decimal("10.00"), applies_to=None, is_active=False)

        class DummyLine:
            def __init__(self, prod):
                self.product = prod

        resolved = resolve_tax(DummyLine(product))
        assert resolved is None
