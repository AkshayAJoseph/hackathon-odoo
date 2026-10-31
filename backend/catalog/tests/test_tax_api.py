import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from accounts.models import User
from catalog.models import Tax, Product

@pytest.mark.django_db
class TestTaxAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(email="admin@brightloop.test", password="Password123!", role="admin")
        self.staff_user = User.objects.create_user(email="staff@brightloop.test", password="Password123!", role="staff")
        self.customer_user = User.objects.create_user(email="cust@brightloop.test", password="Password123!", role="customer")
        self.tax = Tax.objects.create(name="GST 18%", rate_percent=Decimal("18.00"), is_active=True)

    def test_admin_can_create_tax(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post("/api/taxes/", {
            "name": "GST 5%",
            "rate_percent": "5.00",
            "type": "percent",
            "is_active": True
        })
        assert response.status_code == 201
        assert response.data["name"] == "GST 5%"
        assert Decimal(response.data["rate_percent"]) == Decimal("5.00")

    def test_staff_can_read_tax(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get("/api/taxes/")
        assert response.status_code == 200
        assert len(response.data.get("results", response.data)) >= 1

    def test_staff_cannot_create_tax(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post("/api/taxes/", {
            "name": "GST 12%",
            "rate_percent": "12.00",
            "type": "percent"
        })
        assert response.status_code == 403

    def test_customer_cannot_read_tax(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get("/api/taxes/")
        assert response.status_code == 403
