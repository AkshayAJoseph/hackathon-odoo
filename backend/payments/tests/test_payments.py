import pytest
from datetime import date, timedelta
from decimal import Decimal
from rest_framework.test import APIClient
from accounts.models import User
from plans.models import Plan
from subscriptions.models import Subscription
from billing.models import Invoice, InvoiceLine
from payments.models import Payment
from payments.services import record_payment, is_overdue, days_overdue

@pytest.mark.django_db
class TestPaymentsAndOverdue:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(email="admin_pay@brightloop.test", password="Password123!", role="admin")
        self.staff = User.objects.create_user(email="staff_pay@brightloop.test", password="Password123!", role="staff")
        self.cust = User.objects.create_user(email="cust_pay@brightloop.test", password="Password123!", role="customer")

        self.plan = Plan.objects.create(name="Enterprise", price=Decimal("1000.00"), billing_period="monthly")
        self.sub = Subscription.objects.create(
            number="SUB-PAY-01",
            customer=self.cust,
            plan=self.plan,
            start_date=date.today(),
            payment_terms=15,
            status="active"
        )

        self.invoice = Invoice.objects.create(
            number="INV-00999",
            subscription=self.sub,
            customer=self.cust,
            period_start=date.today(),
            period_end=date.today() + timedelta(days=30),
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=15),
            status="confirmed",
            subtotal=Decimal("1000.00"),
            total=Decimal("1000.00"),
            amount_paid=Decimal("0.00")
        )

    def test_partial_payment_keeps_confirmed_and_reduces_balance(self):
        # Must-pass #20: Partial payment -> Stays Confirmed, balance correct
        payment = record_payment(
            invoice=self.invoice,
            method="card",
            amount=Decimal("400.00"),
            date=date.today(),
            note="Deposit",
            user=self.admin
        )
        self.invoice.refresh_from_db()
        assert self.invoice.status == "confirmed"
        assert self.invoice.amount_paid == Decimal("400.00")
        assert self.invoice.balance == Decimal("600.00")

    def test_full_payment_flips_to_paid(self):
        # Must-pass #21: Payments summing to total -> Becomes Paid
        payment = record_payment(
            invoice=self.invoice,
            method="bank_transfer",
            amount=Decimal("1000.00"),
            date=date.today(),
            user=self.staff
        )
        self.invoice.refresh_from_db()
        assert self.invoice.status == "paid"
        assert self.invoice.balance == Decimal("0.00")

    def test_two_payments_summing_to_total_flips_to_paid(self):
        # Must-pass #21
        record_payment(invoice=self.invoice, method="card", amount=Decimal("600.00"))
        self.invoice.refresh_from_db()
        assert self.invoice.status == "confirmed"

        record_payment(invoice=self.invoice, method="upi", amount=Decimal("400.00"))
        self.invoice.refresh_from_db()
        assert self.invoice.status == "paid"
        assert self.invoice.amount_paid == Decimal("1000.00")

    def test_overpayment_rejected_with_clear_message(self):
        # Must-pass #22: Overpayment -> Rejected with clear message
        with pytest.raises(ValueError, match="exceeds outstanding balance"):
            record_payment(invoice=self.invoice, method="card", amount=Decimal("1500.00"))

        # Also after partial payment
        record_payment(invoice=self.invoice, method="card", amount=Decimal("900.00"))
        with pytest.raises(ValueError, match="exceeds outstanding balance"):
            record_payment(invoice=self.invoice, method="cash", amount=Decimal("200.00"))

    def test_payment_on_draft_or_cancelled_rejected(self):
        # Must-pass #23: Invalid method or payment on Draft -> Rejected
        draft_inv = Invoice.objects.create(
            number="INV-DRAFT",
            subscription=self.sub,
            customer=self.cust,
            period_start=date.today() - timedelta(days=60),
            period_end=date.today() - timedelta(days=30),
            due_date=date.today() - timedelta(days=15),
            status="draft",
            total=Decimal("500.00")
        )
        with pytest.raises(ValueError, match="Cannot record payment on a Draft invoice"):
            record_payment(invoice=draft_inv, method="card", amount=Decimal("100.00"))

        cancelled_inv = Invoice.objects.create(
            number="INV-CANCELLED",
            subscription=self.sub,
            customer=self.cust,
            period_start=date.today() - timedelta(days=90),
            period_end=date.today() - timedelta(days=60),
            due_date=date.today() - timedelta(days=45),
            status="cancelled",
            total=Decimal("500.00")
        )
        with pytest.raises(ValueError, match="Cannot record payment on a Cancelled invoice"):
            record_payment(invoice=cancelled_inv, method="card", amount=Decimal("100.00"))

    def test_invalid_payment_method_rejected(self):
        # Must-pass #23: method must be one of card, bank_transfer, upi, cash, cheque
        with pytest.raises(ValueError, match="Invalid payment method"):
            record_payment(invoice=self.invoice, method="bitcoin", amount=Decimal("100.00"))

    def test_overdue_true_only_for_confirmed_past_due_with_balance(self):
        # Must-pass #24: Confirmed, due yesterday, unpaid -> is_overdue true, days_overdue 1
        yesterday = date.today() - timedelta(days=1)
        self.invoice.due_date = yesterday
        self.invoice.save()

        assert is_overdue(self.invoice) is True
        assert days_overdue(self.invoice) == 1

        # Must-pass #25: Paid or not yet due -> is_overdue false
        self.invoice.status = "paid"
        self.invoice.amount_paid = self.invoice.total
        self.invoice.save()
        assert is_overdue(self.invoice) is False
        assert days_overdue(self.invoice) == 0

        # Confirmed but future due date
        self.invoice.status = "confirmed"
        self.invoice.amount_paid = Decimal("0.00")
        self.invoice.due_date = date.today() + timedelta(days=5)
        self.invoice.save()
        assert is_overdue(self.invoice) is False

    def test_payment_api_endpoints(self):
        self.client.force_authenticate(user=self.staff)
        res = self.client.post(f"/api/invoices/{self.invoice.id}/payments/", {
            "method": "upi",
            "amount": "300.00",
            "note": "First installment"
        })
        assert res.status_code == 201
        assert res.data["amount"] == "300.00"

        # List payments
        res_list = self.client.get("/api/payments/")
        assert res_list.status_code == 200
        assert len(res_list.data.get("results", res_list.data)) >= 1
