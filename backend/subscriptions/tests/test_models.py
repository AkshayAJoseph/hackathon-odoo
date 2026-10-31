import pytest
from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from catalog.models import Product, ProductVariant
from plans.models import Plan
from subscriptions.models import Subscription, SubscriptionLine
from subscriptions.services import close_subscription

User = get_user_model()


@pytest.mark.django_db
class TestSubscriptionsModels:
    def test_subscription_creation_and_contracts(self):
        customer = User.objects.create_user(
            email="cust@brightloop.com",
            name="Bright Customer"
        )
        plan = Plan.objects.create(
            name="Standard Monthly",
            price=Decimal("99.00"),
            billing_period="monthly",
            min_quantity=1,
            available_from=date(2026, 1, 1),
            available_to=date(2026, 12, 31),
            auto_close=True,
            closable=True,
            pausable=True,
            renewable=True
        )
        sub = Subscription.objects.create(
            number="SUB-00001",
            customer=customer,
            plan=plan,
            start_date=date(2026, 1, 1),
            expiry_date=date(2026, 1, 31),
            payment_terms=30,
            status="draft",
            is_paused=False,
            next_billing_date=date(2026, 1, 1),
            created_by=customer
        )

        product = Product.objects.create(
            name="Main Seat",
            product_type="service",
            sales_price=Decimal("99.00")
        )
        line = SubscriptionLine.objects.create(
            subscription=sub,
            product=product,
            quantity=2,
            unit_price=Decimal("99.00")
            # tax uses lazy reference 'catalog.Tax', left null until Amrutha's branch merges
        )

        assert sub.id is not None
        assert sub.number == "SUB-00001"
        assert sub.status == "draft"
        assert sub.is_paused is False
        assert sub.lines.count() == 1
        assert line.subtotal == Decimal("198.00")

    def test_close_subscription_stub_callable(self):
        customer = User.objects.create_user(email="c2@brightloop.com", name="C2")
        plan = Plan.objects.create(
            name="P1", price=Decimal("10.00"), billing_period="monthly",
            available_from=date(2026, 1, 1), available_to=date(2026, 12, 31)
        )
        sub = Subscription.objects.create(
            number="SUB-00002",
            customer=customer,
            plan=plan,
            status="active"
        )
        # Service function exposed for Amrutha's auto-close billing engine
        result = close_subscription(sub, user=None)
        assert result.status == "closed"
