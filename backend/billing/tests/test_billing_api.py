import pytest
from decimal import Decimal
from datetime import date
from rest_framework.test import APIClient
from accounts.models import User
from catalog.models import Product
from plans.models import Plan
from subscriptions.models import Subscription, SubscriptionLine

@pytest.mark.django_db
class TestBillingAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(email="admin_bill@brightloop.test", password="Password123!", role="admin")
        self.staff = User.objects.create_user(email="staff_bill@brightloop.test", password="Password123!", role="staff")
        self.customer = User.objects.create_user(email="cust_bill@brightloop.test", password="Password123!", role="customer")

        self.plan = Plan.objects.create(name="Pro Plan", price=Decimal("100.00"), billing_period="monthly")
        self.prod = Product.objects.create(name="Cloud ERP", sales_price=Decimal("100.00"))

        self.sub = Subscription.objects.create(
            number="SUB-API-01",
            customer=self.customer,
            plan=self.plan,
            start_date=date.today(),
            next_billing_date=date.today(),
            status="active"
        )
        SubscriptionLine.objects.create(
            subscription=self.sub,
            product=self.prod,
            quantity=1,
            unit_price=Decimal("100.00")
        )

    def test_admin_can_run_billing(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post("/api/billing/run/", {"as_of": str(date.today())}, format="json")
        assert res.status_code == 200
        assert "created" in res.data
        assert "skipped" in res.data
        assert res.data["created"] == 1

    def test_staff_can_run_billing(self):
        self.client.force_authenticate(user=self.staff)
        res = self.client.post("/api/billing/run/", {}, format="json")
        assert res.status_code == 200

    def test_customer_cannot_run_billing(self):
        self.client.force_authenticate(user=self.customer)
        res = self.client.post("/api/billing/run/", {}, format="json")
        assert res.status_code == 403
