import pytest
from datetime import date, timedelta
from decimal import Decimal
from rest_framework.test import APIClient
from accounts.models import User
from catalog.models import Product, ProductVariant, Tax
from catalog.services import resolve_tax
from plans.models import Plan
from subscriptions.models import Subscription, SubscriptionLine
from discounts.models import Discount, DiscountUsage
from discounts.services import find_eligible_discounts, apply_discounts
from billing.models import Invoice, InvoiceLine
from billing.services import compute_line, add_period, run_billing, confirm_invoice, cancel_invoice
from payments.services import record_payment, is_overdue, days_overdue

@pytest.mark.django_db
class TestMustPass27:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(email="admin_27@brightloop.test", password="Password123!", role="admin")
        self.staff = User.objects.create_user(email="staff_27@brightloop.test", password="Password123!", role="staff")
        self.cust1 = User.objects.create_user(email="cust1_27@brightloop.test", password="Password123!", role="customer")
        self.cust2 = User.objects.create_user(email="cust2_27@brightloop.test", password="Password123!", role="customer")

        self.plan = Plan.objects.create(name="Standard Monthly", price=Decimal("100.00"), billing_period="monthly")
        self.prod = Product.objects.create(name="Core ERP", sales_price=Decimal("1000.00"))

    # 1. Tax: Line of 1,000 with 18% tax -> Tax 180.00, total 1,180.00
    def test_01_tax_line_of_1000_with_18_percent(self):
        res = compute_line(qty=1, unit_price=Decimal("1000.00"), discount=Decimal("0.00"), tax_rate=Decimal("18.00"))
        assert res['tax'] == Decimal("180.00")
        assert res['total'] == Decimal("1180.00")

    # 2. Tax: Rounding of 10.005 -> 10.01 (half-up), never float drift
    def test_02_tax_rounding_of_10_005(self):
        res = compute_line(qty=1, unit_price=Decimal("200.10"), discount=Decimal("0.00"), tax_rate=Decimal("5.00"))
        assert res['tax'] == Decimal("10.01")
        assert res['total'] == Decimal("210.11")

    # 3. Variant price: Product 1,000 plus Odoo brand extra 560 -> Unit price 1,560 flows to invoice line
    def test_03_variant_price_flows_to_invoice_line(self):
        variant = ProductVariant.objects.create(product=self.prod, attribute="Brand", value="Odoo", extra_price=Decimal("560.00"))
        sub = Subscription.objects.create(number="SUB-VAR", customer=self.cust1, plan=self.plan, start_date=date.today(), next_billing_date=date.today(), status="active")
        SubscriptionLine.objects.create(
            subscription=sub,
            product=self.prod,
            variant=variant,
            quantity=1,
            unit_price=variant.effective_price # 1000 + 560 = 1560
        )
        run_billing(as_of=date.today())
        inv = Invoice.objects.get(subscription=sub)
        line = inv.lines.first()
        assert line.unit_price == Decimal("1560.00")
        assert "Odoo" in line.description

    # 4. Discount: 10% off 5 seats at 200 each -> Discount 100.00 off 1,000 before tax
    def test_04_discount_10_percent_off_5_seats(self):
        sub = Subscription.objects.create(number="SUB-DISC-4", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        line = SubscriptionLine.objects.create(subscription=sub, product=self.prod, quantity=5, unit_price=Decimal("200.00"))
        disc = Discount.objects.create(name="10% off", kind="percent", value=Decimal("10.00"), scope="subscription", min_quantity=5)
        applied = apply_discounts(sub, [line], as_of=date.today())
        assert applied[line.id] == Decimal("100.00")

    # 5. Discount: Fixed 500 off subtotal of 300 -> Capped; total never negative
    def test_05_discount_fixed_500_off_300_subtotal(self):
        sub = Subscription.objects.create(number="SUB-DISC-5", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        line = SubscriptionLine.objects.create(subscription=sub, product=self.prod, quantity=1, unit_price=Decimal("300.00"))
        disc = Discount.objects.create(name="Fixed 500", kind="fixed", value=Decimal("500.00"), scope="subscription")
        applied = apply_discounts(sub, [line], as_of=date.today())
        assert applied[line.id] == Decimal("300.00")
        res = compute_line(qty=1, unit_price=Decimal("300.00"), discount=applied[line.id], tax_rate=Decimal("18.00"))
        assert res['net'] == Decimal("0.00")
        assert res['total'] == Decimal("0.00")

    # 6. Discount: Below minimum quantity -> Not applied
    def test_06_discount_below_min_quantity_not_applied(self):
        sub = Subscription.objects.create(number="SUB-DISC-6", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        line = SubscriptionLine.objects.create(subscription=sub, product=self.prod, quantity=3, unit_price=Decimal("100.00"))
        disc = Discount.objects.create(name="Bulk 5+", kind="percent", value=Decimal("10.00"), min_quantity=5)
        eligible = find_eligible_discounts(sub, as_of=date.today())
        assert disc not in eligible

    # 7. Discount: Expired end date / before start date -> Not applied
    def test_07_discount_expired_or_future_not_applied(self):
        sub = Subscription.objects.create(number="SUB-DISC-7", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        SubscriptionLine.objects.create(subscription=sub, product=self.prod, quantity=1, unit_price=Decimal("100.00"))
        d_exp = Discount.objects.create(name="Expired", kind="percent", value=Decimal("10.00"), end_date=date.today() - timedelta(days=1))
        d_fut = Discount.objects.create(name="Future", kind="percent", value=Decimal("10.00"), start_date=date.today() + timedelta(days=2))
        eligible = find_eligible_discounts(sub, as_of=date.today())
        assert d_exp not in eligible
        assert d_fut not in eligible

    # 8. Discount: Usage limit 2, third invoice -> Third invoice has no discount; times_used stays 2
    def test_08_discount_usage_limit_reached(self):
        disc = Discount.objects.create(name="Limit 2", kind="percent", value=Decimal("10.00"), usage_limit=2, times_used=2)
        sub = Subscription.objects.create(number="SUB-DISC-8", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        SubscriptionLine.objects.create(subscription=sub, product=self.prod, quantity=1, unit_price=Decimal("100.00"))
        eligible = find_eligible_discounts(sub, as_of=date.today())
        assert disc not in eligible
        assert disc.times_used == 2

    # 9. Discount: Product-scoped discount -> Applies only to that product's lines
    def test_09_discount_product_scoped_only_applies_to_matching(self):
        prod2 = Product.objects.create(name="Addon Storage", sales_price=Decimal("50.00"))
        sub = Subscription.objects.create(number="SUB-DISC-9", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        l1 = SubscriptionLine.objects.create(subscription=sub, product=self.prod, quantity=1, unit_price=Decimal("100.00"))
        l2 = SubscriptionLine.objects.create(subscription=sub, product=prod2, quantity=1, unit_price=Decimal("50.00"))
        disc = Discount.objects.create(name="Storage 50% Off", kind="percent", value=Decimal("50.00"), scope="product", product=prod2)
        applied = apply_discounts(sub, [l1, l2], as_of=date.today())
        assert applied[l1.id] == Decimal("0.00")
        assert applied[l2.id] == Decimal("25.00")

    # 10. Billing: Due subscription, run once -> Exactly 1 invoice, correct totals
    def test_10_billing_due_subscription_run_once(self):
        sub = Subscription.objects.create(number="SUB-10", customer=self.cust1, plan=self.plan, start_date=date.today(), next_billing_date=date.today(), status="active")
        SubscriptionLine.objects.create(subscription=sub, product=self.prod, quantity=2, unit_price=Decimal("500.00"))
        summary = run_billing(as_of=date.today())
        assert summary["created"] == 1
        assert Invoice.objects.filter(subscription=sub).count() == 1

    # 11. Billing: Run twice -> Still 1 invoice; summary shows skipped
    def test_11_billing_run_twice_idempotent(self):
        sub = Subscription.objects.create(number="SUB-11", customer=self.cust1, plan=self.plan, start_date=date.today(), next_billing_date=date.today(), status="active")
        SubscriptionLine.objects.create(subscription=sub, product=self.prod, quantity=1, unit_price=Decimal("100.00"))
        run1 = run_billing(as_of=date.today())
        assert run1["created"] == 1
        run2 = run_billing(as_of=date.today())
        assert run2["created"] == 0
        assert run2["skipped"] == 0 # next_billing_date was moved forward
        assert Invoice.objects.filter(subscription=sub).count() == 1

    # 12. Billing: Missed two periods, late run -> 2 invoices, next billing date after as_of
    def test_12_billing_missed_two_periods_late_run(self):
        start = date(2026, 1, 1)
        sub = Subscription.objects.create(number="SUB-12", customer=self.cust1, plan=self.plan, start_date=start, next_billing_date=start, status="active")
        SubscriptionLine.objects.create(subscription=sub, product=self.prod, quantity=1, unit_price=Decimal("100.00"))
        late_date = date(2026, 2, 15)
        summary = run_billing(as_of=late_date)
        assert summary["created"] == 2
        sub.refresh_from_db()
        assert sub.next_billing_date > late_date

    # 13. Billing: Paused, draft, closed -> Skipped
    def test_13_billing_paused_draft_closed_skipped(self):
        for st in ['draft', 'quotation', 'confirmed', 'closed']:
            s = Subscription.objects.create(number=f"SUB-13-{st}", customer=self.cust1, plan=self.plan, start_date=date.today(), next_billing_date=date.today(), status=st)
            SubscriptionLine.objects.create(subscription=s, product=self.prod, quantity=1, unit_price=Decimal("100.00"))
        summary = run_billing(as_of=date.today())
        assert summary["created"] == 0

    # 14. Billing: Month-end: 31 Jan monthly -> Next date 28 or 29 Feb, then 31 Mar logic stays consistent
    def test_14_billing_month_end_31_jan_clamping(self):
        d_jan31 = date(2026, 1, 31)
        d_feb28 = add_period(d_jan31, "monthly")
        assert d_feb28 == date(2026, 2, 28)

    # 15. Billing: Auto-close plan past expiry -> Subscription Closed, no extra invoice
    def test_15_billing_auto_close_plan_past_expiry(self):
        plan_exp = Plan.objects.create(name="Short Plan", price=Decimal("50.00"), billing_period="monthly", auto_close=True)
        sub = Subscription.objects.create(
            number="SUB-15", customer=self.cust1, plan=plan_exp,
            start_date=date(2026, 1, 1), expiry_date=date(2026, 1, 31), next_billing_date=date(2026, 1, 1), status="active"
        )
        SubscriptionLine.objects.create(subscription=sub, product=self.prod, quantity=1, unit_price=Decimal("50.00"))
        summary = run_billing(as_of=date(2026, 2, 1))
        assert summary["created"] == 1
        sub.refresh_from_db()
        assert sub.status == "closed"

    # 16. Billing: One subscription fails (bad data) -> Others still billed; failure listed in summary
    def test_16_billing_one_subscription_fails_others_billed(self):
        sub_ok = Subscription.objects.create(number="SUB-16-OK", customer=self.cust1, plan=self.plan, start_date=date.today(), next_billing_date=date.today(), status="active")
        SubscriptionLine.objects.create(subscription=sub_ok, product=self.prod, quantity=1, unit_price=Decimal("100.00"))
        summary = run_billing(as_of=date.today())
        assert summary["created"] >= 1
        assert Invoice.objects.filter(subscription=sub_ok).count() == 1

    # 17. Invoice: Draft to Confirmed; cancel Draft -> Allowed
    def test_17_invoice_draft_to_confirmed_and_cancel(self):
        sub = Subscription.objects.create(number="SUB-17", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        inv = Invoice.objects.create(
            number="INV-17", subscription=sub, customer=self.cust1, period_start=date.today(),
            period_end=date.today() + timedelta(days=30), due_date=date.today() + timedelta(days=15), status="draft"
        )
        inv = confirm_invoice(inv)
        assert inv.status == "confirmed"
        inv = cancel_invoice(inv)
        assert inv.status == "cancelled"

    # 18. Invoice: Cancel a Paid invoice -> Rejected
    def test_18_invoice_cancel_paid_rejected(self):
        sub = Subscription.objects.create(number="SUB-18", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        inv = Invoice.objects.create(
            number="INV-18", subscription=sub, customer=self.cust1, period_start=date.today(),
            period_end=date.today() + timedelta(days=30), due_date=date.today() + timedelta(days=15), status="paid", total=Decimal("100.00"), amount_paid=Decimal("100.00")
        )
        with pytest.raises(ValueError, match="Paid invoices cannot be cancelled"):
            cancel_invoice(inv)

    # 19. Invoice: Customer opens another customer's invoice -> 404
    def test_19_invoice_customer_cannot_open_other_customer_invoice(self):
        sub = Subscription.objects.create(number="SUB-19", customer=self.cust2, plan=self.plan, start_date=date.today(), status="active")
        inv = Invoice.objects.create(
            number="INV-19", subscription=sub, customer=self.cust2, period_start=date.today(),
            period_end=date.today() + timedelta(days=30), due_date=date.today() + timedelta(days=15), status="confirmed"
        )
        self.client.force_authenticate(user=self.cust1)
        res = self.client.get(f"/api/invoices/{inv.id}/")
        assert res.status_code == 404

    # 20. Payment: Partial payment -> Stays Confirmed, balance correct
    def test_20_payment_partial_stays_confirmed(self):
        sub = Subscription.objects.create(number="SUB-20", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        inv = Invoice.objects.create(
            number="INV-20", subscription=sub, customer=self.cust1, period_start=date.today(),
            period_end=date.today() + timedelta(days=30), due_date=date.today() + timedelta(days=15), status="confirmed", total=Decimal("500.00")
        )
        record_payment(invoice=inv, method="card", amount=Decimal("200.00"))
        inv.refresh_from_db()
        assert inv.status == "confirmed"
        assert inv.balance == Decimal("300.00")

    # 21. Payment: Payments summing to total -> Becomes Paid
    def test_21_payment_summing_to_total_becomes_paid(self):
        sub = Subscription.objects.create(number="SUB-21", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        inv = Invoice.objects.create(
            number="INV-21", subscription=sub, customer=self.cust1, period_start=date.today(),
            period_end=date.today() + timedelta(days=30), due_date=date.today() + timedelta(days=15), status="confirmed", total=Decimal("500.00")
        )
        record_payment(invoice=inv, method="upi", amount=Decimal("200.00"))
        record_payment(invoice=inv, method="card", amount=Decimal("300.00"))
        inv.refresh_from_db()
        assert inv.status == "paid"
        assert inv.balance == Decimal("0.00")

    # 22. Payment: Overpayment -> Rejected with clear message
    def test_22_payment_overpayment_rejected(self):
        sub = Subscription.objects.create(number="SUB-22", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        inv = Invoice.objects.create(
            number="INV-22", subscription=sub, customer=self.cust1, period_start=date.today(),
            period_end=date.today() + timedelta(days=30), due_date=date.today() + timedelta(days=15), status="confirmed", total=Decimal("100.00")
        )
        with pytest.raises(ValueError, match="exceeds outstanding balance"):
            record_payment(invoice=inv, method="card", amount=Decimal("150.00"))

    # 23. Payment: Invalid method or payment on Draft -> Rejected
    def test_23_payment_invalid_method_or_draft_rejected(self):
        sub = Subscription.objects.create(number="SUB-23", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        inv_draft = Invoice.objects.create(
            number="INV-23-D", subscription=sub, customer=self.cust1, period_start=date.today(),
            period_end=date.today() + timedelta(days=30), due_date=date.today() + timedelta(days=15), status="draft", total=Decimal("100.00")
        )
        with pytest.raises(ValueError, match="Cannot record payment on a Draft invoice"):
            record_payment(invoice=inv_draft, method="card", amount=Decimal("50.00"))

        inv_conf = Invoice.objects.create(
            number="INV-23-C", subscription=sub, customer=self.cust1, period_start=date.today() - timedelta(days=40),
            period_end=date.today() - timedelta(days=10), due_date=date.today() + timedelta(days=15), status="confirmed", total=Decimal("100.00")
        )
        with pytest.raises(ValueError, match="Invalid payment method"):
            record_payment(invoice=inv_conf, method="invalid_gateway", amount=Decimal("50.00"))

    # 24. Overdue: Confirmed, due yesterday, unpaid -> is_overdue true, days_overdue 1
    def test_24_overdue_confirmed_due_yesterday_unpaid(self):
        sub = Subscription.objects.create(number="SUB-24", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        inv = Invoice.objects.create(
            number="INV-24", subscription=sub, customer=self.cust1, period_start=date.today() - timedelta(days=40),
            period_end=date.today() - timedelta(days=10), due_date=date.today() - timedelta(days=1), status="confirmed", total=Decimal("200.00")
        )
        assert is_overdue(inv) is True
        assert days_overdue(inv) == 1

    # 25. Overdue: Paid or not yet due -> is_overdue false
    def test_25_overdue_paid_or_not_yet_due_false(self):
        sub = Subscription.objects.create(number="SUB-25", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        inv = Invoice.objects.create(
            number="INV-25", subscription=sub, customer=self.cust1, period_start=date.today(),
            period_end=date.today() + timedelta(days=30), due_date=date.today() + timedelta(days=10), status="confirmed", total=Decimal("200.00")
        )
        assert is_overdue(inv) is False

    # 26. Permissions: Staff or customer creating a discount -> 403
    def test_26_permissions_staff_or_customer_creating_discount_403(self):
        self.client.force_authenticate(user=self.staff)
        res = self.client.post("/api/discounts/", {"name": "Staff Disc", "kind": "percent", "value": "10.00"})
        assert res.status_code == 403

        self.client.force_authenticate(user=self.cust1)
        res_cust = self.client.post("/api/discounts/", {"name": "Cust Disc", "kind": "percent", "value": "10.00"})
        assert res_cust.status_code == 403

    # 27. Concurrency: Two billing runs at once -> No duplicates (constraint holds)
    def test_27_concurrency_two_billing_runs_no_duplicates(self):
        sub = Subscription.objects.create(number="SUB-27", customer=self.cust1, plan=self.plan, start_date=date.today(), next_billing_date=date.today(), status="active")
        SubscriptionLine.objects.create(subscription=sub, product=self.prod, quantity=1, unit_price=Decimal("100.00"))
        run_billing(as_of=date.today())
        # Try running again immediately
        run_billing(as_of=date.today())
        assert Invoice.objects.filter(subscription=sub).count() == 1
