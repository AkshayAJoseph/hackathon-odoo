import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from accounts.models import User
from discounts.models import Discount

@pytest.mark.django_db
class TestDiscountAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(email="admin2@brightloop.test", password="Password123!", role="admin")
        self.staff_user = User.objects.create_user(email="staff2@brightloop.test", password="Password123!", role="staff")
        self.customer_user = User.objects.create_user(email="cust2@brightloop.test", password="Password123!", role="customer")
        self.discount = Discount.objects.create(name="10% off", kind="percent", value=Decimal("10.00"), scope="subscription")

    def test_admin_can_crud_discount(self):
        self.client.force_authenticate(user=self.admin_user)
        # Create
        res = self.client.post("/api/discounts/", {
            "name": "Summer Sale",
            "kind": "percent",
            "value": "15.00",
            "scope": "subscription"
        })
        assert res.status_code == 201
        new_id = res.data["id"]

        # List
        res_list = self.client.get("/api/discounts/")
        assert res_list.status_code == 200

        # Update
        res_update = self.client.patch(f"/api/discounts/{new_id}/", {"value": "20.00"})
        assert res_update.status_code == 200
        assert Decimal(res_update.data["value"]) == Decimal("20.00")

    def test_staff_cannot_create_or_read_discount(self):
        # Must-pass #26: staff or customer creating a discount -> 403
        self.client.force_authenticate(user=self.staff_user)
        res_post = self.client.post("/api/discounts/", {
            "name": "Staff Discount",
            "kind": "percent",
            "value": "10.00"
        })
        assert res_post.status_code == 403

        res_get = self.client.get("/api/discounts/")
        assert res_get.status_code == 403

    def test_customer_cannot_access_discount(self):
        self.client.force_authenticate(user=self.customer_user)
        res = self.client.get("/api/discounts/")
        assert res.status_code == 403
