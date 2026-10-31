from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime
from django.db import transaction, connection
from core.models import AuditLog
from payments.models import Payment
from billing.models import Invoice

TWOPLACES = Decimal('0.01')
ALLOWED_METHODS = ['card', 'bank_transfer', 'upi', 'cash', 'cheque']

def quantize_money(amount):
    if amount is None:
        amount = Decimal('0.00')
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    return amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)

def is_overdue(invoice, today=None):
    """
    Confirmed, past due date, balance above zero.
    """
    if today is None:
        today = date.today()
    return bool(invoice.status == 'confirmed' and invoice.due_date < today and invoice.balance > Decimal('0.00'))

def days_overdue(invoice, today=None):
    """
    Number of days past due date if overdue, else 0.
    """
    if today is None:
        today = date.today()
    if is_overdue(invoice, today):
        return (today - invoice.due_date).days
    return 0

def record_payment(invoice, method, amount, payment_date=None, note="", user=None, **kwargs):
    """
    Saves payment, updates amount_paid, flips to Paid when covered,
    rejects overpayment. Safe under concurrency with row lock on Invoice.
    """
    # Support 'date' as keyword argument for backwards compatibility
    if payment_date is None and 'date' in kwargs:
        payment_date = kwargs['date']

    if payment_date is None:
        payment_date = date.today()
    elif isinstance(payment_date, str):
        payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()

    amount = quantize_money(amount)
    if amount <= Decimal('0.00'):
        raise ValueError("Payment amount must be greater than zero.")

    if method not in ALLOWED_METHODS:
        raise ValueError(
            f"Invalid payment method: '{method}'. Allowed methods: {', '.join(ALLOWED_METHODS)}."
        )

    with transaction.atomic():
        # Lock invoice row to prevent concurrent overpayments
        inv_qs = Invoice.objects
        if connection.features.has_select_for_update:
            inv_qs = inv_qs.select_for_update()

        locked_invoice = inv_qs.get(id=invoice.id)

        if locked_invoice.status == 'draft':
            raise ValueError("Cannot record payment on a Draft invoice. Please confirm it first.")
        if locked_invoice.status == 'cancelled':
            raise ValueError("Cannot record payment on a Cancelled invoice.")
        if locked_invoice.status == 'paid':
            raise ValueError("Invoice is already fully paid.")

        outstanding = locked_invoice.balance
        if amount > outstanding:
            raise ValueError(
                f"Overpayment rejected: payment amount (${amount}) exceeds outstanding balance (${outstanding})."
            )

        actor = user if user and getattr(user, 'is_authenticated', False) else None

        payment = Payment.objects.create(
            invoice=locked_invoice,
            method=method,
            amount=amount,
            payment_date=payment_date,
            note=note,
            recorded_by=actor
        )

        new_amount_paid = quantize_money(locked_invoice.amount_paid + amount)
        locked_invoice.amount_paid = new_amount_paid

        if new_amount_paid >= locked_invoice.total:
            old_status = locked_invoice.status
            locked_invoice.status = 'paid'
            locked_invoice.save(update_fields=['amount_paid', 'status', 'updated_at'])
            AuditLog.objects.create(
                actor=actor,
                action='invoice_paid',
                entity='Invoice',
                entity_id=locked_invoice.number,
                from_status=old_status,
                to_status='paid',
                note=f"Paid in full via {method} payment of ${amount}"
            )
        else:
            locked_invoice.save(update_fields=['amount_paid', 'updated_at'])
            AuditLog.objects.create(
                actor=actor,
                action='partial_payment',
                entity='Invoice',
                entity_id=locked_invoice.number,
                from_status=locked_invoice.status,
                to_status=locked_invoice.status,
                note=f"Partial payment of ${amount} via {method}, remaining balance: ${locked_invoice.balance}"
            )

        return payment
