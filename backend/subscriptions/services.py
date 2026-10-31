from datetime import date, timedelta
from decimal import Decimal
import calendar
from django.db import transaction, connection
from rest_framework.exceptions import ValidationError, PermissionDenied
from core.services import log_transition
from core.models import AuditLog
from subscriptions.models import Subscription, SubscriptionLine, SubscriptionSequence

ALLOWED_TRANSITIONS = {
    'draft': ['quotation'],
    'quotation': ['confirmed'],
    'confirmed': ['active'],
    'active': ['closed'],
    'closed': [],
}

def add_period(start_date: date, billing_period: str) -> date:
    """
    Computes the next date after adding one billing period,
    clamping month ends (e.g. 31 Jan + 1 month = 28/29 Feb).
    """
    if billing_period == 'daily':
        return start_date + timedelta(days=1)
    elif billing_period == 'weekly':
        return start_date + timedelta(weeks=1)
    elif billing_period == 'monthly':
        if start_date.month == 12:
            next_year = start_date.year + 1
            next_month = 1
        else:
            next_year = start_date.year
            next_month = start_date.month + 1
        max_days = calendar.monthrange(next_year, next_month)[1]
        next_day = min(start_date.day, max_days)
        return date(next_year, next_month, next_day)
    elif billing_period == 'yearly':
        next_year = start_date.year + 1
        # Handle leap year Feb 29
        if start_date.month == 2 and start_date.day == 29 and not calendar.isleap(next_year):
            return date(next_year, 2, 28)
        return date(next_year, start_date.month, start_date.day)
    return start_date + timedelta(days=30)


def generate_subscription_number() -> str:
    """
    Generates sequential subscription numbers (SUB-00001), concurrency-safe.
    """
    with transaction.atomic():
        seq_qs = SubscriptionSequence.objects
        if connection.features.has_select_for_update:
            seq_qs = seq_qs.select_for_update()
        seq, _ = seq_qs.get_or_create(name='subscription')
        seq.last_number += 1
        seq.save(update_fields=['last_number'])
        return f"SUB-{seq.last_number:05d}"


def create_from_template(template, customer, user, quote_date=None) -> Subscription:
    """
    Turns a quotation template into a Subscription instance.
    Validates plan availability and min_quantity, snapshots line prices,
    sets expiry date based on validity_days, and records an AuditLog.
    """
    quote_date = quote_date or date.today()
    plan = template.plan

    # 1. Validate plan availability
    if plan.available_from and quote_date < plan.available_from:
        raise ValidationError({
            "plan": ["The chosen plan is not available yet as of this quotation date."]
        })
    if plan.available_to and quote_date > plan.available_to:
        raise ValidationError({
            "plan": ["The chosen plan has expired and is no longer available."]
        })

    # 2. Validate plan minimum quantity
    template_lines = list(template.lines.select_related('product', 'variant').all())
    total_qty = sum(tl.quantity for tl in template_lines)
    if total_qty < plan.min_quantity:
        raise ValidationError({
            "quantity": [f"Total line quantity ({total_qty}) does not meet the plan's minimum requirement of {plan.min_quantity}."]
        })

    with transaction.atomic():
        sub_number = generate_subscription_number()
        validity = template.validity_days or 30
        expiry_date = quote_date + timedelta(days=validity)

        sub = Subscription.objects.create(
            number=sub_number,
            customer=customer,
            plan=plan,
            start_date=quote_date,
            expiry_date=expiry_date,
            payment_terms=30,
            status='draft',
            is_paused=False,
            created_by=user if user and getattr(user, 'is_authenticated', False) else None
        )

        for tl in template_lines:
            # Snapshot price: variant effective_price or product sales_price
            if tl.variant:
                unit_price = tl.variant.effective_price
            else:
                unit_price = tl.product.sales_price

            line_total = Decimal(tl.quantity) * unit_price

            SubscriptionLine.objects.create(
                subscription=sub,
                product=tl.product,
                variant=tl.variant,
                quantity=tl.quantity,
                unit_price=unit_price,
                line_total=line_total
            )

        log_transition(
            actor=user if user and getattr(user, 'is_authenticated', False) else None,
            entity='Subscription',
            entity_id=sub.number,
            from_status='',
            to_status='draft'
        )

    return sub


def send_quote(sub: Subscription, user) -> Subscription:
    """Transitions Draft -> Quotation."""
    if sub.status != 'draft':
        raise ValidationError(f"Cannot send quote from status '{sub.status}'. Allowed from 'draft'.")

    from_status = sub.status
    sub.status = 'quotation'
    sub.save(update_fields=['status', 'updated_at'])
    log_transition(user, 'Subscription', sub.number, from_status, 'quotation')
    return sub


def confirm(sub: Subscription, user) -> Subscription:
    """Transitions Quotation -> Confirmed."""
    if sub.status != 'quotation':
        raise ValidationError(f"Cannot confirm subscription from status '{sub.status}'. Allowed from 'quotation'.")

    from_status = sub.status
    sub.status = 'confirmed'
    sub.save(update_fields=['status', 'updated_at'])
    log_transition(user, 'Subscription', sub.number, from_status, 'confirmed')
    return sub


def activate(sub: Subscription, user) -> Subscription:
    """Transitions Confirmed -> Active and primes next_billing_date."""
    if sub.status != 'confirmed':
        raise ValidationError(f"Cannot activate subscription from status '{sub.status}'. Allowed from 'confirmed'.")

    from_status = sub.status
    sub.status = 'active'
    sub.next_billing_date = sub.start_date or date.today()
    sub.save(update_fields=['status', 'next_billing_date', 'updated_at'])
    log_transition(user, 'Subscription', sub.number, from_status, 'active')
    return sub


def close_subscription(sub: Subscription, user=None) -> Subscription:
    """
    Transitions Active -> Closed.
    User-triggered close requires plan.closable=True; billing auto_close allowed anytime.
    """
    if user is not None and not sub.plan.closable:
        raise PermissionDenied("This plan does not permit early manual closure.")

    if sub.status == 'closed':
        return sub

    from_status = sub.status
    sub.status = 'closed'
    sub.save(update_fields=['status', 'updated_at'])
    log_transition(user, 'Subscription', sub.number, from_status, 'closed')
    return sub


def pause(sub: Subscription, user) -> Subscription:
    """Pauses an active subscription without changing its status."""
    if sub.status != 'active':
        raise ValidationError("Only active subscriptions can be paused.")
    if not sub.plan.pausable:
        raise PermissionDenied("This plan does not permit pausing.")

    sub.is_paused = True
    sub.save(update_fields=['is_paused', 'updated_at'])
    AuditLog.objects.create(
        actor=user if user and getattr(user, 'is_authenticated', False) else None,
        action='pause',
        entity='Subscription',
        entity_id=sub.number,
        from_status='active',
        to_status='active',
        note='Subscription paused'
    )
    return sub


def resume(sub: Subscription, user) -> Subscription:
    """Resumes a paused active subscription."""
    if sub.status != 'active':
        raise ValidationError("Only active subscriptions can be resumed.")

    sub.is_paused = False
    sub.save(update_fields=['is_paused', 'updated_at'])
    AuditLog.objects.create(
        actor=user if user and getattr(user, 'is_authenticated', False) else None,
        action='resume',
        entity='Subscription',
        entity_id=sub.number,
        from_status='active',
        to_status='active',
        note='Subscription resumed'
    )
    return sub


def renew(sub: Subscription, user) -> Subscription:
    """Extends the subscription expiry date by one billing period."""
    if not sub.plan.renewable:
        raise PermissionDenied("This plan does not permit renewal.")

    base_date = sub.expiry_date or date.today()
    new_expiry = add_period(base_date, sub.plan.billing_period)
    sub.expiry_date = new_expiry
    sub.save(update_fields=['expiry_date', 'updated_at'])

    AuditLog.objects.create(
        actor=user if user and getattr(user, 'is_authenticated', False) else None,
        action='renew',
        entity='Subscription',
        entity_id=sub.number,
        from_status=sub.status,
        to_status=sub.status,
        note=f'Renewed expiry to {new_expiry}'
    )
    return sub
