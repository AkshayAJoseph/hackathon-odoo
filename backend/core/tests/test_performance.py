import pytest
from decimal import Decimal
from datetime import date
from django.test.utils import CaptureQueriesContext
from django.db import connection
from rest_framework.test import APIClient
from accounts.models import User
from catalog.models import Product, ProductVariant
from plans.models import Plan, QuotationTemplate, TemplateLine
from subscriptions.models import Subscription, SubscriptionLine


@pytest.mark.django_db
class TestEndpointQueryPerformance:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="perf_admin@brightloop.com",
            password="AdminPassword!123",
            name="Perf Admin"
        )
        self.staff = User.objects.create_user(
            email="perf_staff@brightloop.com",
            password="StaffPassword!123",
            name="Perf Staff",
            role="staff",
            is_staff=True
        )
        self.customer = User.objects.create_user(
            email="perf_cust@brightloop.com",
            password="CustPassword!123",
            name="Perf Customer",
            role="customer"
        )

    def test_products_list_query_count_under_10_for_25_items(self):
        # Seed 25 products, each with 2 variants
        products = [
            Product(name=f"Product {i}", product_type="goods", sales_price=Decimal("50.00"))
            for i in range(25)
        ]
        Product.objects.bulk_create(products)
        saved_products = list(Product.objects.all())

        variants = []
        for p in saved_products:
            variants.append(ProductVariant(product=p, attribute="Size", value="M"))
            variants.append(ProductVariant(product=p, attribute="Color", value="Blue"))
        ProductVariant.objects.bulk_create(variants)

        self.client.force_authenticate(user=self.staff)
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get('/api/products')

        assert response.status_code == 200
        num_queries = len(ctx.captured_queries)
        assert num_queries < 10, f"Too many queries for products list: {num_queries}"

    def test_plans_list_query_count_under_10_for_25_items(self):
        plans = [
            Plan(
                name=f"Plan {i}",
                price=Decimal("99.00"),
                billing_period="monthly",
                min_quantity=1
            )
            for i in range(25)
        ]
        Plan.objects.bulk_create(plans)

        self.client.force_authenticate(user=self.staff)
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get('/api/plans')

        assert response.status_code == 200
        num_queries = len(ctx.captured_queries)
        assert num_queries < 10, f"Too many queries for plans list: {num_queries}"

    def test_quotation_templates_list_query_count_under_10_for_25_items(self):
        plan = Plan.objects.create(name="Shared Plan", price=Decimal("100.00"), billing_period="monthly")
        product = Product.objects.create(name="Shared Product", sales_price=Decimal("100.00"))

        templates = [
            QuotationTemplate(name=f"Template {i}", plan=plan, validity_days=30)
            for i in range(25)
        ]
        QuotationTemplate.objects.bulk_create(templates)
        saved_templates = list(QuotationTemplate.objects.all())

        lines = [
            TemplateLine(template=t, product=product, quantity=2)
            for t in saved_templates
        ]
        TemplateLine.objects.bulk_create(lines)

        self.client.force_authenticate(user=self.staff)
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get('/api/quotation-templates')

        assert response.status_code == 200
        num_queries = len(ctx.captured_queries)
        assert num_queries < 10, f"Too many queries for quotation templates list: {num_queries}"

    def test_subscriptions_list_query_count_under_10_for_25_items(self):
        plan = Plan.objects.create(name="Sub Plan", price=Decimal("150.00"), billing_period="monthly")
        product = Product.objects.create(name="Sub Product", sales_price=Decimal("150.00"))

        subs = [
            Subscription(
                number=f"SUB-{i:05d}",
                customer=self.customer,
                plan=plan,
                start_date=date.today(),
                status='active',
                is_paused=False
            )
            for i in range(25)
        ]
        Subscription.objects.bulk_create(subs)
        saved_subs = list(Subscription.objects.all())

        sub_lines = [
            SubscriptionLine(
                subscription=s,
                product=product,
                quantity=1,
                unit_price=Decimal("150.00"),
                line_total=Decimal("150.00")
            )
            for s in saved_subs
        ]
        SubscriptionLine.objects.bulk_create(sub_lines)

        # Authenticate staff (views all 25)
        self.client.force_authenticate(user=self.staff)
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get('/api/subscriptions')

        assert response.status_code == 200
        num_queries = len(ctx.captured_queries)
        assert num_queries < 10, f"Too many queries for subscriptions list: {num_queries}"

    def test_staff_list_query_count_under_10(self):
        # Create 10 staff members
        staff_members = [
            User(
                email=f"staff_{i}@brightloop.com",
                name=f"Staff Member {i}",
                role="staff",
                is_staff=True
            )
            for i in range(10)
        ]
        User.objects.bulk_create(staff_members)

        self.client.force_authenticate(user=self.admin)
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get('/api/staff')

        assert response.status_code == 200
        num_queries = len(ctx.captured_queries)
        assert num_queries < 10, f"Too many queries for staff list: {num_queries}"
