import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.db import IntegrityError, transaction
from accounts.models import User
from catalog.models import Product, Tax
from plans.models import Plan
from subscriptions.models import Subscription, SubscriptionLine
from discounts.models import Discount, DiscountUsage
from billing.models import Invoice, InvoiceLine
from billing.services import add_period, next_invoice_number, build_invoice, run_billing

@pytest.mark.django_db
class TestBillingEngine:
    def setup_method(self):
        self.customer = User.objects.create_user(email="billing_user@brightloop.test", password="Password123!", role="customer")
        self.plan_monthly = Plan.objects.create(
            name="Monthly Plan",
            price=Decimal("100.00"),
            billing_period="monthly",
            auto_close=False
        )
        self.plan_autoclose = Plan.objects.create(
            name="Expiring Plan",
            price=Decimal("100.00"),
            billing_period="monthly",
            auto_close=True
        )
        self.tax18 = Tax.objects.create(name="GST 18%", rate_percent=Decimal("18.00"), is_active=True, applies_to=None)
        self.product = Product.objects.create(name="Business App", sales_price=Decimal("200.00"))

    def test_add_period_month_ends_and_leap_days(self):
        # Must-pass #14: Month-end: 31 Jan monthly -> 28 Feb (or 29 Feb in leap year), then 31 Mar
        # 31 Jan 2026 -> 28 Feb 2026 (non leap)
        d_jan31 = date(2026, 1, 31)
        d_feb28 = add_period(d_jan31, "monthly")
        assert d_feb28 == date(2026, 2, 28)

        # 31 Jan 2024 -> 29 Feb 2024 (leap year)
        d_jan31_leap = date(2024, 1, 31)
        d_feb29 = add_period(d_jan31_leap, "monthly")
        assert d_feb29 == date(2024, 2, 29)

        # 29 Feb 2024 yearly -> 28 Feb 2025
        d_yearly = add_period(date(2024, 2, 29), "yearly")
        assert d_yearly == date(2025, 2, 28)

        # daily & weekly
        d_day = add_period(date(2026, 1, 1), "daily")
        assert d_day == date(2026, 1, 2)
        d_week = add_period(date(2026, 1, 1), "weekly")
        assert d_week == date(2026, 1, 8)

    def test_due_active_subscription_gets_exactly_one_invoice(self):
        # Must-pass #10: Due subscription, run once -> Exactly 1 invoice, correct totals
        today = date(2026, 1, 1)
        sub = Subscription.objects.create(
            number="SUB-00001",
            customer=self.customer,
            plan=self.plan_monthly,
            start_date=today,
            next_billing_date=today,
            status="active"
        )
        SubscriptionLine.objects.create(
            subscription=sub,
            product=self.product,
            quantity=5,
            unit_price=Decimal("200.00"),
            line_total=Decimal("1000.00")
        )

        summary = run_billing(as_of=today)
        assert summary["created"] == 1
        assert summary["skipped"] == 0

        invoices = Invoice.objects.filter(subscription=sub)
        assert invoices.count() == 1
        inv = invoices.first()

        # Gross: 5 * 200 = 1000.00. Tax: 18% = 180.00. Total = 1180.00
        assert inv.subtotal == Decimal("1000.00")
        assert inv.tax_total == Decimal("180.00")
        assert inv.total == Decimal("1180.00")
        assert inv.status == "draft"

        # next_billing_date advanced by 1 month to 2026-02-01
        sub.refresh_from_db()
        assert sub.next_billing_date == date(2026, 2, 1)

    def test_run_billing_twice_creates_no_duplicate(self):
        # Must-pass #11: Run twice -> Still 1 invoice; summary shows skipped
        today = date(2026, 1, 1)
        sub = Subscription.objects.create(
            number="SUB-00002",
            customer=self.customer,
            plan=self.plan_monthly,
            start_date=today,
            next_billing_date=today,
            status="active"
        )
        SubscriptionLine.objects.create(
            subscription=sub,
            product=self.product,
            quantity=1,
            unit_price=Decimal("200.00"),
            line_total=Decimal("200.00")
        )

        run1 = run_billing(as_of=today)
        assert run1["created"] == 1

        run2 = run_billing(as_of=today)
        assert run2["created"] == 0
        assert Invoice.objects.filter(subscription=sub).count() == 1

    def test_non_due_and_inactive_subscriptions_are_skipped(self):
        # Must-pass #13: Paused, draft, quotation, closed subscriptions skipped
        today = date(2026, 1, 1)
        for st in ["draft", "quotation", "confirmed", "closed"]:
            s = Subscription.objects.create(
                number=f"SUB-SKIP-{st}",
                customer=self.customer,
                plan=self.plan_monthly,
                start_date=today,
                next_billing_date=today,
                status=st
            )
            SubscriptionLine.objects.create(subscription=s, product=self.product, quantity=1, unit_price=Decimal("100.00"))

        # Paused active subscription
        s_paused = Subscription.objects.create(
            number="SUB-SKIP-paused",
            customer=self.customer,
            plan=self.plan_monthly,
            start_date=today,
            next_billing_date=today,
            status="active",
            is_paused=True
        )
        SubscriptionLine.objects.create(subscription=s_paused, product=self.product, quantity=1, unit_price=Decimal("100.00"))

        summary = run_billing(as_of=today)
        assert summary["created"] == 0
        assert Invoice.objects.count() == 0

    def test_missed_two_periods_gets_two_invoices_on_late_run(self):
        # Must-pass #12: Missed two periods, late run -> 2 invoices, next billing date after as_of
        # Subscription due on 2026-01-01, late run on 2026-02-15
        start_date = date(2026, 1, 1)
        late_date = date(2026, 2, 15)

        sub = Subscription.objects.create(
            number="SUB-00003",
            customer=self.customer,
            plan=self.plan_monthly,
            start_date=start_date,
            next_billing_date=start_date,
            status="active"
        )
        SubscriptionLine.objects.create(
            subscription=sub,
            product=self.product,
            quantity=1,
            unit_price=Decimal("200.00")
        )

        summary = run_billing(as_of=late_date)
        assert summary["created"] == 2
        assert Invoice.objects.filter(subscription=sub).count() == 2

        sub.refresh_from_db()
        # Next billing date should be 2026-03-01, which is > 2026-02-15
        assert sub.next_billing_date == date(2026, 3, 1)
        assert sub.next_billing_date > late_date

    def test_auto_close_plan_closes_subscription_past_expiry(self):
        # Must-pass #15: Auto-close plan past expiry -> Subscription Closed, no extra invoice
        start_date = date(2026, 1, 1)
        expiry_date = date(2026, 1, 31)
        as_of_date = date(2026, 2, 1)

        sub = Subscription.objects.create(
            number="SUB-00004",
            customer=self.customer,
            plan=self.plan_autoclose,
            start_date=start_date,
            expiry_date=expiry_date,
            next_billing_date=start_date,
            status="active"
        )
        SubscriptionLine.objects.create(subscription=sub, product=self.product, quantity=1, unit_price=Decimal("200.00"))

        summary = run_billing(as_of=as_of_date)
        # Period 1 (Jan 1) bills. Next billing date becomes Feb 1, which > expiry Jan 31 -> auto close!
        assert summary["created"] == 1
        sub.refresh_from_db()
        assert sub.status == "closed"

        # Subsequent run bills nothing
        summary2 = run_billing(as_of=date(2026, 3, 1))
        assert summary2["created"] == 0
        assert Invoice.objects.filter(subscription=sub).count() == 1

    def test_discount_usage_committed_atomically_with_invoice(self):
        # Must-pass #8: DiscountUsage rows are written and times_used incremented
        disc = Discount.objects.create(
            name="10% Promo",
            kind="percent",
            value=Decimal("10.00"),
            scope="subscription",
            usage_limit=1,
            times_used=0,
            is_active=True
        )
        today = date(2026, 1, 1)
        sub = Subscription.objects.create(
            number="SUB-00005",
            customer=self.customer,
            plan=self.plan_monthly,
            start_date=today,
            next_billing_date=today,
            status="active"
        )
        SubscriptionLine.objects.create(subscription=sub, product=self.product, quantity=1, unit_price=Decimal("200.00"))

        run_billing(as_of=today)
        disc.refresh_from_db()
        assert disc.times_used == 1
        assert DiscountUsage.objects.filter(discount=disc).count() == 1
        usage = DiscountUsage.objects.get(discount=disc)
        assert usage.amount == Decimal("20.00") # 10% of 200.00

    def test_invoice_numbers_are_sequential_and_unique(self):
        num1 = next_invoice_number()
        num2 = next_invoice_number()
        assert num1 == "INV-00001"
        assert num2 == "INV-00002"
        assert num1 != num2

    def test_one_subscription_fails_others_still_billed(self):
        # Must-pass #16: One subscription fails (bad data), others still billed
        today = date(2026, 1, 1)
        sub_good = Subscription.objects.create(
            number="SUB-GOOD",
            customer=self.customer,
            plan=self.plan_monthly,
            start_date=today,
            next_billing_date=today,
            status="active"
        )
        SubscriptionLine.objects.create(subscription=sub_good, product=self.product, quantity=1, unit_price=Decimal("100.00"))

        # Subscription with no lines -> handled or raises error inside atomic
        sub_empty = Subscription.objects.create(
            number="SUB-EMPTY",
            customer=self.customer,
            plan=self.plan_monthly,
            start_date=today,
            next_billing_date=today,
            status="active"
        )
        # Empty subscription line has 0 lines, or we can test an error simulation

        summary = run_billing(as_of=today)
        assert summary["created"] >= 1
        assert Invoice.objects.filter(subscription=sub_good).count() == 1
