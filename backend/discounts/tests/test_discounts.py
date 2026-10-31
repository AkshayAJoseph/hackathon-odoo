import pytest
from datetime import date, timedelta
from decimal import Decimal
from accounts.models import User
from catalog.models import Product
from plans.models import Plan
from subscriptions.models import Subscription, SubscriptionLine
from discounts.models import Discount
from discounts.services import find_eligible_discounts, apply_discounts

@pytest.mark.django_db
class TestDiscountServices:
    def setup_method(self):
        self.customer = User.objects.create_user(email="client@test.com", password="Password123!", role="customer")
        self.plan = Plan.objects.create(name="Pro Plan", price=Decimal("100.00"), billing_period="monthly")
        self.prod1 = Product.objects.create(name="Seat", sales_price=Decimal("200.00"))
        self.prod2 = Product.objects.create(name="Storage", sales_price=Decimal("50.00"))

        self.sub = Subscription.objects.create(
            number="SUB-00100",
            customer=self.customer,
            plan=self.plan,
            start_date=date.today(),
            status="active"
        )
        self.line1 = SubscriptionLine.objects.create(
            subscription=self.sub,
            product=self.prod1,
            quantity=5,
            unit_price=Decimal("200.00"),
            line_total=Decimal("1000.00")
        )

    def test_percent_discount_10_percent_off_5_seats(self):
        # Must-pass #4: 10% off 5 seats at 200 each -> Discount 100.00 off 1,000 before tax
        disc = Discount.objects.create(
            name="10% off seats",
            kind="percent",
            value=Decimal("10.00"),
            scope="subscription",
            min_quantity=5,
            is_active=True
        )
        eligible = find_eligible_discounts(self.sub, as_of=date.today())
        assert disc in eligible

        discounts_applied = apply_discounts(self.sub, [self.line1], as_of=date.today())
        assert discounts_applied[self.line1.id] == Decimal("100.00")

    def test_fixed_discount_capped_never_negative(self):
        # Must-pass #5: Fixed 500 off subtotal of 300 -> Capped; total never negative
        sub_small = Subscription.objects.create(
            number="SUB-00101",
            customer=self.customer,
            plan=self.plan,
            start_date=date.today(),
            status="active"
        )
        small_line = SubscriptionLine.objects.create(
            subscription=sub_small,
            product=self.prod2,
            quantity=6,
            unit_price=Decimal("50.00"),
            line_total=Decimal("300.00")
        )
        disc = Discount.objects.create(
            name="Fixed 500 off",
            kind="fixed",
            value=Decimal("500.00"),
            scope="subscription",
            is_active=True
        )
        eligible = find_eligible_discounts(sub_small, as_of=date.today())
        assert disc in eligible

        applied = apply_discounts(sub_small, [small_line], as_of=date.today())
        assert applied[small_line.id] == Decimal("300.00") # Capped at line gross 300

    def test_below_minimum_quantity(self):
        # Must-pass #6: Below min quantity -> Not applied
        Discount.objects.create(
            name="Bulk 10+",
            kind="percent",
            value=Decimal("15.00"),
            scope="subscription",
            min_quantity=10,
            is_active=True
        )
        eligible = find_eligible_discounts(self.sub, as_of=date.today())
        assert len(eligible) == 0

    def test_expired_end_date_and_before_start_date(self):
        # Must-pass #7: Expired end date / before start date -> Not applied
        today = date.today()
        # Expired
        Discount.objects.create(
            name="Past Discount",
            kind="percent",
            value=Decimal("20.00"),
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=1),
            is_active=True
        )
        # Future
        Discount.objects.create(
            name="Future Discount",
            kind="percent",
            value=Decimal("20.00"),
            start_date=today + timedelta(days=5),
            end_date=today + timedelta(days=30),
            is_active=True
        )
        eligible = find_eligible_discounts(self.sub, as_of=today)
        assert len(eligible) == 0

    def test_usage_limit_reached(self):
        # Must-pass #8: Usage limit 2, third invoice -> Not applied when limit reached
        disc = Discount.objects.create(
            name="Limited",
            kind="percent",
            value=Decimal("10.00"),
            usage_limit=2,
            times_used=2,
            is_active=True
        )
        eligible = find_eligible_discounts(self.sub, as_of=date.today())
        assert disc not in eligible

    def test_product_scoped_discount(self):
        # Must-pass #9: Product-scoped discount applies only to that product's lines
        line2 = SubscriptionLine.objects.create(
            subscription=self.sub,
            product=self.prod2,
            quantity=2,
            unit_price=Decimal("50.00"),
            line_total=Decimal("100.00")
        )
        disc_prod1 = Discount.objects.create(
            name="20% off seats only",
            kind="percent",
            value=Decimal("20.00"),
            scope="product",
            product=self.prod1,
            is_active=True
        )
        applied = apply_discounts(self.sub, [self.line1, line2], as_of=date.today())
        # Line 1 (prod1, gross 1000) gets 20% = 200.00
        assert applied[self.line1.id] == Decimal("200.00")
        # Line 2 (prod2, gross 100) gets 0.00
        assert applied[line2.id] == Decimal("0.00")

    def test_best_discount_wins_when_two_qualify(self):
        # 10% vs fixed 150 off on 1000 subtotal -> 150 wins (150 > 100)
        Discount.objects.create(
            name="10% off",
            kind="percent",
            value=Decimal("10.00"),
            scope="subscription",
            is_active=True
        )
        Discount.objects.create(
            name="150 off",
            kind="fixed",
            value=Decimal("150.00"),
            scope="subscription",
            is_active=True
        )
        applied = apply_discounts(self.sub, [self.line1], as_of=date.today())
        assert applied[self.line1.id] == Decimal("150.00")
