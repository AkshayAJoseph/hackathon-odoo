import pytest
from datetime import date, timedelta
from decimal import Decimal
from rest_framework.test import APIClient
from accounts.models import User
from catalog.models import Product
from plans.models import Plan
from subscriptions.models import Subscription, SubscriptionLine
from billing.models import Invoice, InvoiceLine
from billing.services import confirm_invoice, cancel_invoice, mark_sent

@pytest.mark.django_db
class TestInvoiceActions:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(email="admin_inv@brightloop.test", password="Password123!", role="admin")
        self.staff = User.objects.create_user(email="staff_inv@brightloop.test", password="Password123!", role="staff")
        self.cust1 = User.objects.create_user(email="cust1@brightloop.test", password="Password123!", role="customer")
        self.cust2 = User.objects.create_user(email="cust2@brightloop.test", password="Password123!", role="customer")

        self.plan = Plan.objects.create(name="Business Plan", price=Decimal("150.00"), billing_period="monthly")
        self.sub1 = Subscription.objects.create(number="SUB-CUST1", customer=self.cust1, plan=self.plan, start_date=date.today(), status="active")
        self.sub2 = Subscription.objects.create(number="SUB-CUST2", customer=self.cust2, plan=self.plan, start_date=date.today(), status="active")

        self.inv1 = Invoice.objects.create(
            number="INV-00101",
            subscription=self.sub1,
            customer=self.cust1,
            period_start=date.today(),
            period_end=date.today() + timedelta(days=30),
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=15),
            status="draft",
            total=Decimal("150.00"),
            amount_paid=Decimal("0.00")
        )
        InvoiceLine.objects.create(invoice=self.inv1, description="Business Plan", quantity=1, unit_price=Decimal("150.00"), line_total=Decimal("150.00"))

        self.inv2 = Invoice.objects.create(
            number="INV-00102",
            subscription=self.sub2,
            customer=self.cust2,
            period_start=date.today(),
            period_end=date.today() + timedelta(days=30),
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=15),
            status="draft",
            total=Decimal("150.00"),
            amount_paid=Decimal("0.00")
        )

    def test_draft_to_confirmed_and_cancel_draft(self):
        # Must-pass #17: Draft to Confirmed; cancel Draft Allowed
        inv = confirm_invoice(self.inv1, actor=self.admin)
        assert inv.status == "confirmed"

        # Cancel confirmed
        inv_cancelled = cancel_invoice(inv, actor=self.admin)
        assert inv_cancelled.status == "cancelled"

    def test_cancel_paid_invoice_is_rejected(self):
        # Must-pass #18: Cancel a Paid invoice -> Rejected
        self.inv1.status = "paid"
        self.inv1.save()

        with pytest.raises(ValueError, match="Paid invoices cannot be cancelled"):
            cancel_invoice(self.inv1, actor=self.admin)

    def test_customer_cannot_open_another_customer_invoice(self):
        # Must-pass #19: Customer opens another customer's invoice -> 404
        self.client.force_authenticate(user=self.cust1)
        res = self.client.get(f"/api/invoices/{self.inv2.id}/")
        assert res.status_code == 404

        # But can open own invoice
        res_own = self.client.get(f"/api/invoices/{self.inv1.id}/")
        assert res_own.status_code == 200
        assert res_own.data["number"] == "INV-00101"

    def test_invoice_list_customer_isolation(self):
        self.client.force_authenticate(user=self.cust1)
        res = self.client.get("/api/invoices/")
        assert res.status_code == 200
        results = res.data.get("results", res.data)
        assert len(results) == 1
        assert results[0]["id"] == self.inv1.id

    def test_invoice_confirm_cancel_send_endpoints(self):
        self.client.force_authenticate(user=self.staff)
        res_confirm = self.client.post(f"/api/invoices/{self.inv1.id}/confirm/")
        assert res_confirm.status_code == 200
        assert res_confirm.data["status"] == "confirmed"

        res_send = self.client.post(f"/api/invoices/{self.inv1.id}/send/")
        assert res_send.status_code == 200
        assert res_send.data["sent_at"] is not None

        res_cancel = self.client.post(f"/api/invoices/{self.inv1.id}/cancel/")
        assert res_cancel.status_code == 200
        assert res_cancel.data["status"] == "cancelled"

    def test_invoice_print_html_view(self):
        self.client.force_authenticate(user=self.cust1)
        res = self.client.get(f"/api/invoices/{self.inv1.id}/print/")
        assert res.status_code == 200
        assert "text/html" in res["Content-Type"]
        assert "INV-00101" in res.content.decode("utf-8")
        assert "Brightloop" in res.content.decode("utf-8")
