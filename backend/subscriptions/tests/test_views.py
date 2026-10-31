import pytest
from datetime import date
from decimal import Decimal
from rest_framework.test import APIClient
from accounts.models import User
from catalog.models import Product, ProductVariant
from plans.models import Plan, QuotationTemplate, TemplateLine
from subscriptions.models import Subscription, SubscriptionLine
from subscriptions.services import create_from_template


@pytest.mark.django_db
class TestSubscriptionViewsAndActions:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email="admin_sub@brightloop.com", password="AdminPassword!123", name="Sub Admin")
        self.staff = User.objects.create_user(email="staff_sub@brightloop.com", password="StaffPassword!123", name="Sub Staff", role="staff", is_staff=True)
        self.cust1 = User.objects.create_user(email="cust1_sub@brightloop.com", password="CustPassword!123", name="Customer One", role="customer")
        self.cust2 = User.objects.create_user(email="cust2_sub@brightloop.com", password="CustPassword!123", name="Customer Two", role="customer")

        self.plan = Plan.objects.create(
            name="Professional Monthly",
            price=Decimal("200.00"),
            billing_period="monthly",
            min_quantity=1,
            available_from=date(2026, 1, 1),
            available_to=date(2026, 12, 31),
            auto_close=False,
            closable=True,
            pausable=True,
            renewable=True
        )
        self.prod = Product.objects.create(name="Pro License", product_type="software", sales_price=Decimal("200.00"))
        self.template = QuotationTemplate.objects.create(name="Pro 1-Seat Template", plan=self.plan, validity_days=30)
        TemplateLine.objects.create(template=self.template, product=self.prod, quantity=1)

    def test_allowed_actions_serialization_in_each_state(self):
        self.client.force_authenticate(user=self.staff)
        sub = create_from_template(self.template, self.cust1, self.staff)

        # 1. Draft
        res = self.client.get(f'/api/subscriptions/{sub.id}')
        assert res.status_code == 200
        assert res.json()["allowed_actions"] == ["send_quote"]

        # 2. Quotation
        self.client.post(f'/api/subscriptions/{sub.id}/send-quote')
        res = self.client.get(f'/api/subscriptions/{sub.id}')
        assert res.json()["allowed_actions"] == ["confirm"]

        # 3. Confirmed
        self.client.post(f'/api/subscriptions/{sub.id}/confirm')
        res = self.client.get(f'/api/subscriptions/{sub.id}')
        assert res.json()["allowed_actions"] == ["activate"]

        # 4. Active (unpaused)
        self.client.post(f'/api/subscriptions/{sub.id}/activate')
        res = self.client.get(f'/api/subscriptions/{sub.id}')
        actions = res.json()["allowed_actions"]
        assert "pause" in actions
        assert "close" in actions
        assert "renew" in actions
        assert "resume" not in actions

        # 5. Active (paused)
        self.client.post(f'/api/subscriptions/{sub.id}/pause')
        res = self.client.get(f'/api/subscriptions/{sub.id}')
        actions_paused = res.json()["allowed_actions"]
        assert "resume" in actions_paused
        assert "pause" not in actions_paused

        # 6. Closed
        self.client.post(f'/api/subscriptions/{sub.id}/resume')
        self.client.post(f'/api/subscriptions/{sub.id}/close')
        res = self.client.get(f'/api/subscriptions/{sub.id}')
        assert res.json()["allowed_actions"] == []

    def test_customer_isolation_returns_404_for_other_customer_resource(self):
        sub1 = create_from_template(self.template, self.cust1, self.staff)
        sub2 = create_from_template(self.template, self.cust2, self.staff)

        # Customer 1 accesses their own -> 200
        self.client.force_authenticate(user=self.cust1)
        res_own = self.client.get(f'/api/subscriptions/{sub1.id}')
        assert res_own.status_code == 200
        assert res_own.json()["number"] == sub1.number

        # Customer 1 accesses Customer 2's subscription -> 404 (Akhila contract: prevent ID probing)
        res_other = self.client.get(f'/api/subscriptions/{sub2.id}')
        assert res_other.status_code == 404

        # Customer 1 list endpoint only contains sub1
        res_list = self.client.get('/api/subscriptions')
        assert res_list.status_code == 200
        items = res_list.json().get("results", res_list.json())
        assert len(items) == 1
        assert items[0]["id"] == sub1.id

    def test_template_to_subscription_action_endpoint(self):
        self.client.force_authenticate(user=self.staff)
        res = self.client.post(f'/api/quotation-templates/{self.template.id}/create-subscription', {
            "customer": self.cust1.id
        }, format='json')
        assert res.status_code == 201
        data = res.json()
        assert data["number"].startswith("SUB-")
        assert data["status"] == "draft"
        assert data["allowed_actions"] == ["send_quote"]
        assert len(data["lines"]) == 1
        assert data["lines"][0]["unit_price"] == "200.00"

    def test_renew_action_endpoint(self):
        self.client.force_authenticate(user=self.staff)
        sub = create_from_template(self.template, self.cust1, self.staff)
        self.client.post(f'/api/subscriptions/{sub.id}/send-quote')
        self.client.post(f'/api/subscriptions/{sub.id}/confirm')
        self.client.post(f'/api/subscriptions/{sub.id}/activate')

        orig_expiry = sub.expiry_date
        res_renew = self.client.post(f'/api/subscriptions/{sub.id}/renew')
        assert res_renew.status_code == 200
        assert res_renew.json()["expiry_date"] > str(orig_expiry)
