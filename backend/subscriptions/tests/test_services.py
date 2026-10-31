import pytest
from datetime import date, timedelta
from decimal import Decimal
from rest_framework.exceptions import ValidationError, PermissionDenied
from accounts.models import User
from catalog.models import Product, ProductVariant
from plans.models import Plan, QuotationTemplate, TemplateLine
from core.models import AuditLog
from subscriptions.models import Subscription, SubscriptionLine
from subscriptions.services import (
    generate_subscription_number,
    create_from_template,
    send_quote,
    confirm,
    activate,
    close_subscription,
    pause,
    resume,
    renew,
    ALLOWED_TRANSITIONS,
)


@pytest.mark.django_db
class TestSubscriptionServicesAndFSM:
    def setup_method(self):
        self.admin = User.objects.create_superuser(email="admin_fsm@brightloop.com", password="AdminPassword!123", name="FSM Admin")
        self.customer = User.objects.create_user(email="cust_fsm@brightloop.com", password="CustPassword!123", name="FSM Cust")

        self.plan = Plan.objects.create(
            name="Standard Plan",
            price=Decimal("100.00"),
            billing_period="monthly",
            min_quantity=2,
            available_from=date(2026, 1, 1),
            available_to=date(2026, 12, 31),
            auto_close=False,
            closable=True,
            pausable=True,
            renewable=True
        )
        self.product = Product.objects.create(name="Seat", product_type="software", sales_price=Decimal("1000.00"))
        self.variant = ProductVariant.objects.create(product=self.product, attribute="brand", value="Odoo", extra_price=Decimal("560.00"))

        self.template = QuotationTemplate.objects.create(
            name="Standard 2-Seat Odoo Quote",
            plan=self.plan,
            validity_days=15
        )
        self.t_line = TemplateLine.objects.create(
            template=self.template,
            product=self.product,
            variant=self.variant,
            quantity=2
        )

    def test_sequential_number_generation(self):
        n1 = generate_subscription_number()
        n2 = generate_subscription_number()
        assert n1.startswith("SUB-")
        assert n2.startswith("SUB-")
        assert int(n2.split("-")[1]) == int(n1.split("-")[1]) + 1

    def test_create_from_template_snapshots_price_and_sets_dates(self):
        quote_date = date(2026, 3, 1)
        sub = create_from_template(
            template=self.template,
            customer=self.customer,
            user=self.admin,
            quote_date=quote_date
        )

        assert sub.id is not None
        assert sub.customer == self.customer
        assert sub.plan == self.plan
        assert sub.status == "draft"
        assert sub.start_date == quote_date
        assert sub.expiry_date == quote_date + timedelta(days=15)
        assert sub.lines.count() == 1

        line = sub.lines.first()
        assert line.quantity == 2
        # Snapshot price: Product (1,000) + Variant (560) = 1,560.00
        assert line.unit_price == Decimal("1560.00")

        # Mutate catalog prices
        self.product.sales_price = Decimal("2000.00")
        self.product.save()
        self.variant.extra_price = Decimal("800.00")
        self.variant.save()

        # Existing subscription unit price MUST remain snapshotted at 1560.00
        line.refresh_from_db()
        assert line.unit_price == Decimal("1560.00")

        # AuditLog recorded
        log = AuditLog.objects.filter(entity="Subscription", entity_id=sub.number).first()
        assert log is not None
        assert log.to_status == "draft"

    def test_create_from_template_validates_min_quantity(self):
        # Plan requires min_quantity = 2. Create template with quantity 1
        bad_template = QuotationTemplate.objects.create(name="Bad 1-Seat", plan=self.plan, validity_days=10)
        TemplateLine.objects.create(template=bad_template, product=self.product, quantity=1)

        with pytest.raises(ValidationError) as exc_info:
            create_from_template(bad_template, self.customer, self.admin)
        assert "min_quantity" in str(exc_info.value.detail) or "quantity" in str(exc_info.value.detail).lower()

    def test_create_from_template_validates_plan_availability_dates(self):
        # Plan available 2026-01-01 to 2026-12-31. Attempt creation on 2027-01-01
        future_date = date(2027, 1, 1)
        with pytest.raises(ValidationError) as exc_info:
            create_from_template(self.template, self.customer, self.admin, quote_date=future_date)
        assert "available" in str(exc_info.value.detail).lower()

    def test_fsm_happy_path_transitions_and_audit_logging(self):
        sub = create_from_template(self.template, self.customer, self.admin, quote_date=date(2026, 3, 1))
        assert sub.status == "draft"

        # 1. Draft -> Quotation
        sub = send_quote(sub, self.admin)
        assert sub.status == "quotation"
        log1 = AuditLog.objects.filter(entity="Subscription", entity_id=sub.number, to_status="quotation").first()
        assert log1 is not None

        # 2. Quotation -> Confirmed
        sub = confirm(sub, self.admin)
        assert sub.status == "confirmed"
        log2 = AuditLog.objects.filter(entity="Subscription", entity_id=sub.number, to_status="confirmed").first()
        assert log2 is not None

        # 3. Confirmed -> Active
        sub = activate(sub, self.admin)
        assert sub.status == "active"
        assert sub.next_billing_date == sub.start_date
        log3 = AuditLog.objects.filter(entity="Subscription", entity_id=sub.number, to_status="active").first()
        assert log3 is not None

        # 4. Active -> Closed
        sub = close_subscription(sub, self.admin)
        assert sub.status == "closed"
        log4 = AuditLog.objects.filter(entity="Subscription", entity_id=sub.number, to_status="closed").first()
        assert log4 is not None

    def test_fsm_illegal_transitions_rejected(self):
        sub = create_from_template(self.template, self.customer, self.admin)
        assert sub.status == "draft"

        # Illegal jump: Draft directly to Active
        with pytest.raises(ValidationError):
            activate(sub, self.admin)

        # Illegal jump: Draft directly to Confirmed
        with pytest.raises(ValidationError):
            confirm(sub, self.admin)

    def test_fsm_pause_and_resume_requires_pausable_plan(self):
        sub = create_from_template(self.template, self.customer, self.admin)
        send_quote(sub, self.admin)
        confirm(sub, self.admin)
        activate(sub, self.admin)

        # Plan is pausable
        assert sub.is_paused is False
        sub = pause(sub, self.admin)
        assert sub.is_paused is True
        assert sub.status == "active"  # Status remains active when paused

        sub = resume(sub, self.admin)
        assert sub.is_paused is False

        # Non-pausable plan rejects pause
        sub.plan.pausable = False
        sub.plan.save()
        with pytest.raises(PermissionDenied):
            pause(sub, self.admin)

    def test_fsm_close_subscription_respects_closable_flag_for_users(self):
        sub = create_from_template(self.template, self.customer, self.admin)
        send_quote(sub, self.admin)
        confirm(sub, self.admin)
        activate(sub, self.admin)

        sub.plan.closable = False
        sub.plan.save()

        # User close attempt on non-closable plan returns 403 / PermissionDenied
        with pytest.raises(PermissionDenied):
            close_subscription(sub, user=self.admin)

        # Billing engine auto_close (user=None) is allowed
        sub = close_subscription(sub, user=None)
        assert sub.status == "closed"

    def test_fsm_renew_extends_expiry_date_by_billing_period(self):
        sub = create_from_template(self.template, self.customer, self.admin, quote_date=date(2026, 1, 1))
        initial_expiry = sub.expiry_date  # 2026-01-16
        send_quote(sub, self.admin)
        confirm(sub, self.admin)
        activate(sub, self.admin)

        sub = renew(sub, self.admin)
        # Monthly plan extends expiry date by 1 month
        assert sub.expiry_date > initial_expiry

        # Non-renewable plan rejects renew
        sub.plan.renewable = False
        sub.plan.save()
        with pytest.raises(PermissionDenied):
            renew(sub, self.admin)
