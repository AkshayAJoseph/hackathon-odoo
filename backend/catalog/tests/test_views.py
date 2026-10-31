import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from accounts.models import User
from catalog.models import Product, ProductVariant


@pytest.mark.django_db
class TestCatalogAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin_cat@brightloop.com",
            password="AdminPassword!123",
            name="Admin User"
        )
        self.staff = User.objects.create_user(
            email="staff_cat@brightloop.com",
            password="StaffPassword!123",
            name="Staff User",
            role="staff",
            is_staff=True
        )
        self.customer = User.objects.create_user(
            email="cust_cat@brightloop.com",
            password="CustPassword!123",
            name="Cust User",
            role="customer"
        )

    def test_products_list_and_create_permissions(self):
        # 1. Anonymous gets 401
        res = self.client.get('/api/products')
        assert res.status_code == 401

        # 2. Customer gets 403
        self.client.force_authenticate(user=self.customer)
        assert self.client.get('/api/products').status_code == 403
        assert self.client.post('/api/products', {
            "name": "Product 1",
            "product_type": "software",
            "sales_price": "100.00"
        }, format='json').status_code == 403

        # 3. Staff gets 200 on read, 403 on write
        self.client.force_authenticate(user=self.staff)
        assert self.client.get('/api/products').status_code == 200
        assert self.client.post('/api/products', {
            "name": "Product 1",
            "product_type": "software",
            "sales_price": "100.00"
        }, format='json').status_code == 403

        # 4. Admin gets 201 on write
        self.client.force_authenticate(user=self.admin)
        res_post = self.client.post('/api/products', {
            "name": "ERP Suite",
            "product_type": "software",
            "sales_price": "1000.00",
            "cost_price": "400.00",
            "notes": "Enterprise core license"
        }, format='json')
        assert res_post.status_code == 201
        data = res_post.json()
        assert data["name"] == "ERP Suite"
        assert data["sales_price"] == "1000.00"
        assert data["cost_price"] == "400.00"

    def test_product_variants_crud_and_effective_price(self):
        product = Product.objects.create(
            name="CRM Professional",
            product_type="software",
            sales_price=Decimal("1000.00"),
            cost_price=Decimal("300.00")
        )

        # Staff cannot create variant
        self.client.force_authenticate(user=self.staff)
        res_staff = self.client.post(f'/api/products/{product.id}/variants', {
            "attribute": "brand",
            "value": "Odoo",
            "extra_price": "560.00"
        }, format='json')
        assert res_staff.status_code == 403

        # Admin can create variant
        self.client.force_authenticate(user=self.admin)
        res_admin = self.client.post(f'/api/products/{product.id}/variants', {
            "attribute": "brand",
            "value": "Odoo",
            "extra_price": "560.00"
        }, format='json')
        assert res_admin.status_code == 201
        data = res_admin.json()
        assert data["attribute"] == "brand"
        assert data["value"] == "Odoo"
        assert data["extra_price"] == "560.00"
        # Effective price = 1000.00 + 560.00 = 1560.00 (string with 2 decimals)
        assert data["effective_price"] == "1560.00"

        # GET product detail includes nested variants
        res_get = self.client.get(f'/api/products/{product.id}')
        assert res_get.status_code == 200
        p_data = res_get.json()
        assert len(p_data["variants"]) == 1
        assert p_data["variants"][0]["effective_price"] == "1560.00"
