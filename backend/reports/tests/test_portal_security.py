import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from plans.models import Plan
from catalog.models import Product
from subscriptions.models import Subscription, SubscriptionLine
from billing.models import Invoice

User = get_user_model()

@pytest.mark.django_db
class TestCustomerPortalSecurity:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.customer1 = User.objects.create_user(email="c1@portal.test", password="Password123!", role="customer")
        self.customer2 = User.objects.create_user(email="c2@portal.test", password="Password123!", role="customer")
        self.plan = Plan.objects.create(name="Monthly Plan", billing_period="monthly", price=Decimal('50.00'))
        self.prod = Product.objects.create(name="Seats", sales_price=Decimal('50.00'))

        # Subscriptions for customer 1
        self.sub1 = Subscription.objects.create(
            number="SUB-C1-001", customer=self.customer1, plan=self.plan, start_date=date.today(), status="active"
        )
        SubscriptionLine.objects.create(
            subscription=self.sub1, product=self.prod, quantity=1, unit_price=Decimal('50.00'), line_total=Decimal('50.00')
        )

        # Subscriptions for customer 2
        self.sub2 = Subscription.objects.create(
            number="SUB-C2-001", customer=self.customer2, plan=self.plan, start_date=date.today(), status="active"
        )

        # Invoices for customer 1
        self.inv1 = Invoice.objects.create(
            number="INV-C1-001", subscription=self.sub1, customer=self.customer1,
            period_start=date.today(), period_end=date.today() + timedelta(days=30),
            due_date=date.today() + timedelta(days=15), status="confirmed", total=Decimal('50.00')
        )

        # Invoices for customer 2
        self.inv2 = Invoice.objects.create(
            number="INV-C2-001", subscription=self.sub2, customer=self.customer2,
            period_start=date.today(), period_end=date.today() + timedelta(days=30),
            due_date=date.today() + timedelta(days=15), status="confirmed", total=Decimal('100.00')
        )

    def test_customer_cannot_see_other_customer_subscriptions(self):
        client = APIClient()
        client.force_authenticate(user=self.customer1)

        # List should only contain customer1's subscription
        res = client.get('/api/portal/subscriptions/')
        assert res.status_code == 200
        numbers = [item['number'] for item in res.data.get('results', res.data)]
        assert "SUB-C1-001" in numbers
        assert "SUB-C2-001" not in numbers

        # Detail view for customer2's sub should return 404
        res_other = client.get(f'/api/portal/subscriptions/{self.sub2.id}/')
        assert res_other.status_code == 404

    def test_customer_cannot_see_or_print_other_customer_invoices(self):
        client = APIClient()
        client.force_authenticate(user=self.customer1)

        # List should only contain customer1's invoices
        res = client.get('/api/portal/invoices/')
        assert res.status_code == 200
        numbers = [item['number'] for item in res.data.get('results', res.data)]
        assert "INV-C1-001" in numbers
        assert "INV-C2-001" not in numbers

        # Direct detail access for customer 2's invoice must return 404
        res_detail = client.get(f'/api/portal/invoices/{self.inv2.id}/')
        assert res_detail.status_code == 404

        # Accessing /api/invoices/{id}/ directly as customer 1 on customer 2's invoice also returns 404
        res_main_invoice = client.get(f'/api/invoices/{self.inv2.id}/')
        assert res_main_invoice.status_code == 404

    def test_unauthenticated_blocked(self):
        client = APIClient()
        assert client.get('/api/portal/subscriptions/').status_code == 401
        assert client.get('/api/portal/invoices/').status_code == 401

