from decimal import Decimal
import datetime
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from plans.models import Plan
from catalog.models import Product
from subscriptions.models import Subscription, SubscriptionLine
from billing.models import Invoice
from payments.models import Payment
from reports.services import (
    calculate_subscription_mrr,
    calculate_arr_from_mrr,
    get_dashboard_summary,
    compute_mrr_for_active_subscriptions,
    get_revenue_by_month,
    get_overdue_invoices_report,
)

User = get_user_model()

@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email="admin@test.com",
        password="Password123!",
        role="admin"
    )

@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        email="staff@test.com",
        password="Password123!",
        role="staff"
    )

@pytest.fixture
def customer_user(db):
    return User.objects.create_user(
        email="customer@test.com",
        password="Password123!",
        role="customer"
    )

@pytest.fixture
def sample_data(db, customer_user):
    today = datetime.date.today()
    # 1. Plans
    plan_monthly = Plan.objects.create(name="Pro Monthly", billing_period="monthly", price=Decimal('100.00'))
    plan_yearly = Plan.objects.create(name="Enterprise Yearly", billing_period="yearly", price=Decimal('1200.00'))

    # 2. Product
    prod = Product.objects.create(name="Cloud Platform", sales_price=Decimal('100.00'), cost_price=Decimal('20.00'))

    # 3. Subscriptions
    # Active monthly sub: 100/mo -> MRR 100.00
    sub1 = Subscription.objects.create(
        number="SUB-00001",
        customer=customer_user,
        plan=plan_monthly,
        start_date=today,
        status="active"
    )
    SubscriptionLine.objects.create(
        subscription=sub1,
        product=prod,
        quantity=1,
        unit_price=Decimal('100.00'),
        line_total=Decimal('100.00')
    )

    # Active yearly sub: 1200/yr -> MRR 100.00
    sub2 = Subscription.objects.create(
        number="SUB-00002",
        customer=customer_user,
        plan=plan_yearly,
        start_date=today,
        status="active"
    )
    SubscriptionLine.objects.create(
        subscription=sub2,
        product=prod,
        quantity=1,
        unit_price=Decimal('1200.00'),
        line_total=Decimal('1200.00')
    )

    # Paused monthly sub: 50/mo -> should NOT be included in MRR
    sub3 = Subscription.objects.create(
        number="SUB-00003",
        customer=customer_user,
        plan=plan_monthly,
        start_date=today,
        status="active",
        is_paused=True
    )
    SubscriptionLine.objects.create(
        subscription=sub3,
        product=prod,
        quantity=1,
        unit_price=Decimal('50.00'),
        line_total=Decimal('50.00')
    )

    # 4. Invoices
    # Confirmed, not overdue invoice
    inv1 = Invoice.objects.create(
        number="INV-00001",
        subscription=sub1,
        customer=customer_user,
        period_start=today,
        period_end=today + datetime.timedelta(days=30),
        issue_date=today,
        due_date=today + datetime.timedelta(days=15),
        status="confirmed",
        total=Decimal('100.00'),
        amount_paid=Decimal('0.00')
    )

    # Confirmed, OVERDUE invoice: due 5 days ago, total 200, paid 50 -> outstanding 150
    inv2 = Invoice.objects.create(
        number="INV-00002",
        subscription=sub1,
        customer=customer_user,
        period_start=today - datetime.timedelta(days=35),
        period_end=today - datetime.timedelta(days=5),
        issue_date=today - datetime.timedelta(days=35),
        due_date=today - datetime.timedelta(days=5),
        status="confirmed",
        total=Decimal('200.00'),
        amount_paid=Decimal('50.00')
    )

    # Paid invoice: total 300, paid 300
    inv3 = Invoice.objects.create(
        number="INV-00003",
        subscription=sub2,
        customer=customer_user,
        period_start=today - datetime.timedelta(days=60),
        period_end=today - datetime.timedelta(days=30),
        issue_date=today - datetime.timedelta(days=60),
        due_date=today - datetime.timedelta(days=30),
        status="paid",
        total=Decimal('300.00'),
        amount_paid=Decimal('300.00')
    )

    # 5. Payments
    Payment.objects.create(
        invoice=inv2,
        method="card",
        amount=Decimal('50.00'),
        payment_date=today - datetime.timedelta(days=2)
    )
    Payment.objects.create(
        invoice=inv3,
        method="bank_transfer",
        amount=Decimal('300.00'),
        payment_date=today - datetime.timedelta(days=30)
    )

    return {
        "sub1": sub1,
        "sub2": sub2,
        "sub3": sub3,
        "inv1": inv1,
        "inv2": inv2,
        "inv3": inv3,
    }


def test_hand_computed_dashboard_figures(sample_data):
    # Hand calculation:
    # Active subs: 3 (sub1, sub2, sub3 are all status='active')
    # Unpaused active subs MRR:
    # sub1 (monthly 100) -> 100.00
    # sub2 (yearly 1200) -> 100.00
    # sub3 is paused -> 0.00
    # Total MRR = 200.00, ARR = 2400.00
    #
    # Revenue collected: 50.00 + 300.00 = 350.00
    #
    # Total outstanding on Confirmed invoices:
    # inv1: 100.00 - 0.00 = 100.00
    # inv2: 200.00 - 50.00 = 150.00
    # Total outstanding = 250.00
    #
    # Overdue on Confirmed invoices (due_date < today and amount_paid < total):
    # inv2 only: count = 1, amount = 150.00
    summary = get_dashboard_summary(use_cache=False)

    assert summary["active_subscriptions"] == 3
    assert summary["mrr"] == "200.00"
    assert summary["arr"] == "2400.00"
    assert summary["revenue_collected"] == "350.00"
    assert summary["total_outstanding"] == "250.00"
    assert summary["overdue_count"] == 1
    assert summary["overdue_amount"] == "150.00"

    # Verify all monetary values are returned as strings (no float drift)
    for key in ["mrr", "arr", "revenue_collected", "total_outstanding", "overdue_amount"]:
        assert isinstance(summary[key], str)


@pytest.mark.django_db
def test_reports_endpoints_rbac(admin_user, staff_user, customer_user, sample_data):
    client = APIClient()

    # Public / Unauthenticated gets 401
    res = client.get('/api/reports/summary/')
    assert res.status_code == 401

    # Customer gets 403 (RBAC enforcement)
    client.force_authenticate(user=customer_user)
    res = client.get('/api/reports/summary/')
    assert res.status_code == 403

    # Staff gets 200
    client.force_authenticate(user=staff_user)
    res = client.get('/api/reports/summary/')
    assert res.status_code == 200
    assert res.data["mrr"] == "200.00"

    # Admin gets 200
    client.force_authenticate(user=admin_user)
    res_summary = client.get('/api/reports/summary/')
    assert res_summary.status_code == 200

    res_rev = client.get('/api/reports/revenue/')
    assert res_rev.status_code == 200

    res_overdue = client.get('/api/reports/overdue/')
    assert res_overdue.status_code == 200
    assert len(res_overdue.data) == 1
    assert res_overdue.data[0]["number"] == "INV-00002"

    res_csv = client.get('/api/reports/export.csv?type=overdue')
    assert res_csv.status_code == 200
    assert 'text/csv' in res_csv['Content-Type']
    assert 'INV-00002' in res_csv.content.decode('utf-8')
