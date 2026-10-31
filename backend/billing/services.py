import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction, connection
from django.utils import timezone
from core.models import AuditLog
from catalog.services import resolve_tax
from subscriptions.models import Subscription
from discounts.services import get_best_eligible_discount
from discounts.models import DiscountUsage
from billing.models import Invoice, InvoiceLine, InvoiceSequence

TWOPLACES = Decimal('0.01')

def quantize_money(amount):
    if amount is None:
        amount = Decimal('0.00')
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    return amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)

def compute_line(qty, unit_price, discount=Decimal('0.00'), tax_rate=Decimal('0.00')):
    """
    Net, tax and total for one line, rounded half-up to 2 places.
    Discount is applied before tax and capped so line net never goes below zero.
    """
    qty = Decimal(str(qty))
    unit_price = quantize_money(unit_price)
    discount = quantize_money(discount)
    tax_rate = Decimal(str(tax_rate))

    gross = quantize_money(qty * unit_price)

    # Discount capped so line net never goes below zero
    actual_discount = min(discount, gross)
    net = quantize_money(gross - actual_discount)

    # Tax calculated on net
    raw_tax = (net * tax_rate) / Decimal('100')
    tax_amount = quantize_money(raw_tax)

    total = quantize_money(net + tax_amount)

    return {
        'quantity': int(qty),
        'unit_price': unit_price,
        'discount': actual_discount,
        'net': net,
        'tax_rate': tax_rate,
        'tax': tax_amount,
        'total': total,
    }

def add_period(start_date, billing_period):
    """
    Next billing date for daily, weekly, monthly, yearly.
    Clamps month ends, so 31 Jan plus one month is 28 or 29 Feb.
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
        day = min(start_date.day, max_days)
        return date(next_year, next_month, day)
    elif billing_period == 'yearly':
        next_year = start_date.year + 1
        max_days = calendar.monthrange(next_year, start_date.month)[1]
        day = min(start_date.day, max_days)
        return date(next_year, start_date.month, day)
    else:
        raise ValueError(f"Unknown billing period: {billing_period}")

def next_invoice_number():
    """
    Sequential INV-00001, safe under concurrency (DB row lock with select_for_update).
    """
    with transaction.atomic():
        seq_qs = InvoiceSequence.objects
        if connection.features.has_select_for_update:
            seq_qs = seq_qs.select_for_update()
        seq, _ = seq_qs.get_or_create(name='invoice')
        seq.last_number += 1
        seq.save(update_fields=['last_number'])
        return f"INV-{seq.last_number:05d}"

def build_invoice(subscription, period_start):
    """
    Creates Invoice and InvoiceLines with taxes and discounts applied,
    writes DiscountUsage rows and increments times_used atomically.
    """
    with transaction.atomic():
        next_date = add_period(period_start, subscription.plan.billing_period)
        period_end = next_date - timedelta(days=1)
        issue_date = date.today()
        due_date = issue_date + timedelta(days=subscription.payment_terms)

        inv_num = next_invoice_number()
        invoice = Invoice.objects.create(
            number=inv_num,
            subscription=subscription,
            customer=subscription.customer,
            period_start=period_start,
            period_end=period_end,
            issue_date=issue_date,
            due_date=due_date,
            status='draft',
            subtotal=Decimal('0.00'),
            discount_total=Decimal('0.00'),
            tax_total=Decimal('0.00'),
            total=Decimal('0.00'),
            amount_paid=Decimal('0.00'),
        )

        sub_lines = list(subscription.lines.all())
        best_discount, line_discounts, total_discount = get_best_eligible_discount(
            subscription, sub_lines, as_of=period_start
        )

        total_subtotal = Decimal('0.00')
        total_discount_amount = Decimal('0.00')
        total_tax_amount = Decimal('0.00')
        total_invoice_amount = Decimal('0.00')

        for s_line in sub_lines:
            tax = resolve_tax(s_line)
            tax_rate = tax.rate_percent if tax else Decimal('0.00')
            line_disc = line_discounts.get(s_line.id, Decimal('0.00'))

            comp = compute_line(
                qty=s_line.quantity,
                unit_price=s_line.unit_price,
                discount=line_disc,
                tax_rate=tax_rate
            )

            desc = s_line.product.name
            if s_line.variant:
                desc += f" ({s_line.variant.value})"

            InvoiceLine.objects.create(
                invoice=invoice,
                product=s_line.product,
                description=desc,
                quantity=s_line.quantity,
                unit_price=comp['unit_price'],
                discount=comp['discount'],
                tax_rate=comp['tax_rate'],
                tax_amount=comp['tax'],
                line_total=comp['total']
            )

            total_subtotal += comp['unit_price'] * comp['quantity']
            total_discount_amount += comp['discount']
            total_tax_amount += comp['tax']
            total_invoice_amount += comp['total']

        invoice.subtotal = quantize_money(total_subtotal)
        invoice.discount_total = quantize_money(total_discount_amount)
        invoice.tax_total = quantize_money(total_tax_amount)
        invoice.total = quantize_money(total_invoice_amount)
        invoice.save()

        # If discount applied, write DiscountUsage and increment times_used atomically
        if best_discount and invoice.discount_total > Decimal('0.00'):
            DiscountUsage.objects.create(
                discount=best_discount,
                invoice=invoice,
                subscription=subscription,
                amount=invoice.discount_total
            )
            best_discount.times_used += 1
            best_discount.save(update_fields=['times_used'])

        AuditLog.objects.create(
            actor=None,
            action='create_invoice',
            entity='Invoice',
            entity_id=invoice.number,
            from_status='',
            to_status='draft',
            note=f"Created for subscription {subscription.number} ({period_start} - {period_end})"
        )

        return invoice

def confirm_invoice(invoice, actor=None):
    """
    Validated status change: Draft -> Confirmed. Writes AuditLog row.
    """
    if invoice.status != 'draft':
        raise ValueError(f"Cannot confirm invoice in '{invoice.status}' status (must be 'draft').")

    with transaction.atomic():
        invoice.status = 'confirmed'
        invoice.save(update_fields=['status', 'updated_at'])
        AuditLog.objects.create(
            actor=actor if actor and getattr(actor, 'is_authenticated', False) else None,
            action='confirm_invoice',
            entity='Invoice',
            entity_id=invoice.number,
            from_status='draft',
            to_status='confirmed',
            note='Invoice confirmed'
        )
    return invoice

def cancel_invoice(invoice, actor=None):
    """
    Validated status change: Draft or Confirmed -> Cancelled.
    Paid invoices CANNOT be cancelled. Writes AuditLog row.
    """
    if invoice.status == 'paid':
        raise ValueError("Paid invoices cannot be cancelled.")
    if invoice.status not in ['draft', 'confirmed']:
        raise ValueError(f"Cannot cancel invoice in '{invoice.status}' status.")

    with transaction.atomic():
        from_status = invoice.status
        invoice.status = 'cancelled'
        invoice.save(update_fields=['status', 'updated_at'])
        AuditLog.objects.create(
            actor=actor if actor and getattr(actor, 'is_authenticated', False) else None,
            action='cancel_invoice',
            entity='Invoice',
            entity_id=invoice.number,
            from_status=from_status,
            to_status='cancelled',
            note='Invoice cancelled'
        )
    return invoice

def mark_sent(invoice, actor=None):
    """
    Sets sent_at timestamp and logs audit entry.
    """
    with transaction.atomic():
        invoice.sent_at = timezone.now()
        invoice.save(update_fields=['sent_at', 'updated_at'])
        AuditLog.objects.create(
            actor=actor if actor and getattr(actor, 'is_authenticated', False) else None,
            action='mark_sent',
            entity='Invoice',
            entity_id=invoice.number,
            from_status=invoice.status,
            to_status=invoice.status,
            note='Invoice marked as sent'
        )
    return invoice

def run_billing(as_of=None):
    """
    Bills every due, active, unpaused subscription;
    idempotent; catches up missed periods; auto-closes expired plans.
    Uses transaction.atomic per subscription and select_for_update(skip_locked=True).
    Returns summary dict: {created, skipped, failed:[{subscription, reason}]}.
    """
    if as_of is None:
        as_of = date.today()
    elif isinstance(as_of, str):
        as_of = datetime.strptime(as_of, "%Y-%m-%d").date()

    summary = {
        'created': 0,
        'skipped': 0,
        'failed': []
    }

    # Select candidate subscriptions
    qs = Subscription.objects.filter(status='active', is_paused=False, next_billing_date__lte=as_of)
    with transaction.atomic():
        if connection.features.has_select_for_update_skip_locked:
            qs = qs.select_for_update(skip_locked=True)
        elif connection.features.has_select_for_update:
            qs = qs.select_for_update()
        due_subscriptions = list(qs)

    for sub in due_subscriptions:
        try:
            with transaction.atomic():
                # Re-fetch with row lock
                sub_qs = Subscription.objects
                if connection.features.has_select_for_update:
                    sub_qs = sub_qs.select_for_update()
                sub = sub_qs.get(id=sub.id)
                if sub.status != 'active' or sub.is_paused or not sub.next_billing_date:
                    continue

                while sub.next_billing_date and sub.next_billing_date <= as_of:
                    # Check auto-close if beyond expiry before billing
                    if sub.expiry_date and sub.next_billing_date > sub.expiry_date:
                        if sub.plan.auto_close:
                            sub.status = 'closed'
                            sub.save(update_fields=['status'])
                            AuditLog.objects.create(
                                action='close_subscription',
                                entity='Subscription',
                                entity_id=sub.number,
                                from_status='active',
                                to_status='closed',
                                note='Auto-closed past expiry'
                            )
                        break

                    period_start = sub.next_billing_date

                    # Idempotency check: unique constraint on (subscription, period_start)
                    if Invoice.objects.filter(subscription=sub, period_start=period_start).exists():
                        summary['skipped'] += 1
                    else:
                        build_invoice(sub, period_start)
                        summary['created'] += 1

                    # Advance next_billing_date
                    next_date = add_period(period_start, sub.plan.billing_period)
                    sub.next_billing_date = next_date

                    # Auto-close check after billing
                    if sub.plan.auto_close and sub.expiry_date and sub.next_billing_date > sub.expiry_date:
                        sub.status = 'closed'
                        AuditLog.objects.create(
                            action='close_subscription',
                            entity='Subscription',
                            entity_id=sub.number,
                            from_status='active',
                            to_status='closed',
                            note='Auto-closed past expiry'
                        )
                        sub.save()
                        break

                    sub.save()

        except Exception as e:
            summary['failed'].append({
                'subscription': sub.number,
                'reason': str(e)
            })

    return summary
