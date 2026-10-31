import pytest
from datetime import date
from decimal import Decimal
from rest_framework.test import APIClient
from accounts.models import User
from plans.models import Plan


@pytest.mark.django_db
class TestPlansAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin_plan@brightloop.com",
            password="AdminPassword!123",
            name="Plan Admin"
        )
        self.staff = User.objects.create_user(
            email="staff_plan@brightloop.com",
            password="StaffPassword!123",
            name="Plan Staff",
            role="staff",
            is_staff=True
        )
        self.customer = User.objects.create_user(
            email="cust_plan@brightloop.com",
            password="CustPassword!123",
            name="Plan Customer",
            role="customer"
        )

    def test_plans_permissions_and_crud(self):
        # 1. Anonymous gets 401
        assert self.client.get('/api/plans').status_code == 401

        # 2. Customer gets 403
        self.client.force_authenticate(user=self.customer)
        assert self.client.get('/api/plans').status_code == 403
        assert self.client.post('/api/plans', {
            "name": "P1", "price": "10.00", "billing_period": "monthly",
            "available_from": "2026-01-01", "available_to": "2026-12-31"
        }, format='json').status_code == 403

        # 3. Staff reads 200, writes 403
        self.client.force_authenticate(user=self.staff)
        assert self.client.get('/api/plans').status_code == 200
        assert self.client.post('/api/plans', {
            "name": "P1", "price": "10.00", "billing_period": "monthly",
            "available_from": "2026-01-01", "available_to": "2026-12-31"
        }, format='json').status_code == 403

        # 4. Admin creates plan -> 201 Created
        self.client.force_authenticate(user=self.admin)
        res_post = self.client.post('/api/plans', {
            "name": "Enterprise Annual Plan",
            "price": "1200.00",
            "billing_period": "yearly",
            "min_quantity": 5,
            "available_from": "2026-01-01",
            "available_to": "2026-12-31",
            "auto_close": False,
            "closable": True,
            "pausable": True,
            "renewable": True
        }, format='json')
        assert res_post.status_code == 201
        data = res_post.json()
        assert data["name"] == "Enterprise Annual Plan"
        assert data["price"] == "1200.00"
        assert data["billing_period"] == "yearly"
        assert data["min_quantity"] == 5

    def test_plan_date_validation_rejected(self):
        self.client.force_authenticate(user=self.admin)
        res_bad = self.client.post('/api/plans', {
            "name": "Invalid Date Plan",
            "price": "50.00",
            "billing_period": "monthly",
            "available_from": "2026-06-01",
            "available_to": "2026-05-01"  # Invalid
        }, format='json')
        assert res_bad.status_code == 400
        assert "available_to" in res_bad.json() or "non_field_errors" in res_bad.json()

    def test_quotation_templates_permissions_and_crud(self):
        from catalog.models import Product, ProductVariant
        plan = Plan.objects.create(
            name="Plan For Quote",
            price=Decimal("100.00"),
            billing_period="monthly",
            available_from=date(2026, 1, 1),
            available_to=date(2026, 12, 31)
        )
        prod = Product.objects.create(name="Seat", product_type="service", sales_price=Decimal("100.00"))
        var = ProductVariant.objects.create(product=prod, attribute="tier", value="Gold", extra_price=Decimal("20.00"))

        # 1. Customer gets 403
        self.client.force_authenticate(user=self.customer)
        assert self.client.get('/api/quotation-templates').status_code == 403
        assert self.client.post('/api/quotation-templates', {
            "name": "Quote 1", "plan": plan.id, "validity_days": 30
        }, format='json').status_code == 403

        # 2. Staff gets 200/201 (Staff & Admin can read/write quotation templates)
        self.client.force_authenticate(user=self.staff)
        res_staff_create = self.client.post('/api/quotation-templates', {
            "name": "Staff Quote Template",
            "plan": plan.id,
            "validity_days": 15,
            "notes": "Created by sales staff",
            "lines": [
                {
                    "product": prod.id,
                    "variant": var.id,
                    "quantity": 3
                }
            ]
        }, format='json')
        assert res_staff_create.status_code == 201
        q_data = res_staff_create.json()
        assert q_data["name"] == "Staff Quote Template"
        assert len(q_data["lines"]) == 1
        assert q_data["lines"][0]["quantity"] == 3
        assert q_data["lines"][0]["product"] == prod.id

        # 3. List templates with select_related / prefetch
        res_list = self.client.get('/api/quotation-templates')
        assert res_list.status_code == 200
        items = res_list.json().get("results", res_list.json())
        assert any(t["name"] == "Staff Quote Template" for t in items)
