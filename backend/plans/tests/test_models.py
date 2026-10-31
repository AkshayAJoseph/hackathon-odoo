import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from catalog.models import Product, ProductVariant
from plans.models import Plan, QuotationTemplate, TemplateLine


@pytest.mark.django_db
class TestPlansModels:
    def test_plan_creation_and_attributes(self):
        plan = Plan.objects.create(
            name="Monthly Professional",
            price=Decimal("49.99"),
            billing_period="monthly",
            min_quantity=1,
            available_from=date(2026, 1, 1),
            available_to=date(2026, 12, 31),
            auto_close=False,
            closable=True,
            pausable=True,
            renewable=True
        )
        assert plan.id is not None
        assert plan.name == "Monthly Professional"
        assert plan.billing_period == "monthly"
        assert plan.auto_close is False

    def test_plan_date_validation_available_to_before_from(self):
        plan = Plan(
            name="Invalid Plan",
            price=Decimal("10.00"),
            billing_period="monthly",
            min_quantity=1,
            available_from=date(2026, 6, 1),
            available_to=date(2026, 5, 1)  # Invalid: to < from
        )
        with pytest.raises(ValidationError):
            plan.clean()

    def test_quotation_template_and_template_lines(self):
        plan = Plan.objects.create(
            name="Enterprise Annual",
            price=Decimal("1200.00"),
            billing_period="yearly",
            min_quantity=5,
            available_from=date(2026, 1, 1),
            available_to=date(2026, 12, 31),
        )
        product = Product.objects.create(
            name="User Seat License",
            product_type="service",
            sales_price=Decimal("200.00")
        )
        variant = ProductVariant.objects.create(
            product=product,
            attribute="edition",
            value="Enterprise",
            extra_price=Decimal("50.00")
        )

        template = QuotationTemplate.objects.create(
            name="Standard 5-Seat Enterprise Quote",
            plan=plan,
            validity_days=15
        )
        line = TemplateLine.objects.create(
            template=template,
            product=product,
            variant=variant,
            quantity=5
        )

        assert template.id is not None
        assert template.validity_days == 15
        assert template.lines.count() == 1
        assert line.quantity == 5
        assert line.variant.value == "Enterprise"
