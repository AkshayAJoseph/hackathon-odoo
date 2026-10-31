import pytest
from decimal import Decimal
from catalog.models import Product, ProductVariant


@pytest.mark.django_db
class TestCatalogModels:
    def test_product_creation_and_attributes(self):
        product = Product.objects.create(
            name="Business Software Core",
            product_type="service",
            sales_price=Decimal("1000.00"),
            cost_price=Decimal("400.00"),
            notes="Base subscription license"
        )
        assert product.id is not None
        assert product.name == "Business Software Core"
        assert product.sales_price == Decimal("1000.00")
        assert product.cost_price == Decimal("400.00")

    def test_product_variant_effective_price_calculation(self):
        product = Product.objects.create(
            name="ERP Suite",
            product_type="service",
            sales_price=Decimal("1000.00"),
            cost_price=Decimal("300.00"),
        )
        variant = ProductVariant.objects.create(
            product=product,
            attribute="brand",
            value="Odoo",
            extra_price=Decimal("560.00")
        )
        assert variant.id is not None
        # Effective price = sales_price + extra_price (1000 + 560 = 1560)
        assert variant.effective_price == Decimal("1560.00")
        assert str(variant) == "ERP Suite - brand: Odoo (+560.00)"

    def test_variant_with_zero_extra_price(self):
        product = Product.objects.create(
            name="Basic Addon",
            product_type="service",
            sales_price=Decimal("250.00")
        )
        variant = ProductVariant.objects.create(
            product=product,
            attribute="tier",
            value="Standard",
            extra_price=Decimal("0.00")
        )
        assert variant.effective_price == Decimal("250.00")
