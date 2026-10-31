import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional, List
from django.db.models import Sum, Count, Q, F, DecimalField, Value
from django.db.models.functions import Coalesce, TruncMonth
from django.core.cache import cache
from subscriptions.models import Subscription
from billing.models import Invoice
from payments.models import Payment

DAILY_FACTOR = Decimal('365') / Decimal('12')
WEEKLY_FACTOR = Decimal('52') / Decimal('12')
MONTHLY_FACTOR = Decimal('1')
YEARLY_FACTOR = Decimal('1') / Decimal('12')


def calculate_subscription_mrr(recurring_total: Decimal, billing_period: str) -> Decimal:
    """
    Normalise recurring subscription amount to MRR according to SPEC 5.9:
    - Monthly: total / 1
    - Yearly: total / 12
    - Weekly: total * 52 / 12
    - Daily: total * 365 / 12
    All results rounded using ROUND_HALF_UP to 2 decimal places.
    """
    if recurring_total is None or recurring_total <= Decimal('0'):
        return Decimal('0.00')

    period = billing_period.lower()
    if period == 'monthly':
        mrr = recurring_total * MONTHLY_FACTOR
    elif period == 'yearly':
        mrr = recurring_total * YEARLY_FACTOR
    elif period == 'weekly':
        mrr = recurring_total * WEEKLY_FACTOR
    elif period == 'daily':
        mrr = recurring_total * DAILY_FACTOR
    else:
        raise ValueError(f"Unsupported billing period for MRR calculation: {billing_period}")

    return mrr.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_arr_from_mrr(mrr: Decimal) -> Decimal:
    """ARR is MRR * 12."""
    if mrr is None:
        return Decimal('0.00')
    arr = mrr * Decimal('12')
    return arr.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def compute_mrr_for_active_subscriptions(
    plan_id: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Decimal:
    """
    Computes exact total MRR over active, unpaused subscriptions.
    Groups by plan billing period and aggregates lines in pure SQL.
    """
    qs = Subscription.objects.filter(status='active', is_paused=False)
    if plan_id:
        qs = qs.filter(plan_id=plan_id)
    if customer_id:
        qs = qs.filter(customer_id=customer_id)

    # Aggregate line sums grouped by plan billing period
    # lines.line_total contains snapshotted recurring amounts
    period_aggregates = qs.values('plan__billing_period').annotate(
        total_recurring=Coalesce(Sum('lines__line_total'), Value(Decimal('0.00'), output_field=DecimalField()))
    )

    total_mrr = Decimal('0.00')
    for item in period_aggregates:
        period = item['plan__billing_period']
        amount = item['total_recurring'] or Decimal('0.00')
        if period:
            total_mrr += calculate_subscription_mrr(amount, period)

    return total_mrr.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def get_dashboard_summary(
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    plan_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Dashboard reporting aggregation service with a 60-second cache.
    Uses pure SQL aggregate() without Python row iteration.
    All monetary amounts returned formatted as 2-decimal strings.
    """
    cache_key = f"dashboard_summary_{start_date}_{end_date}_{plan_id}_{customer_id}"
    if use_cache:
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

    # 1. Active Subscriptions count & MRR / ARR
    subs_qs = Subscription.objects.all()
    if plan_id:
        subs_qs = subs_qs.filter(plan_id=plan_id)
    if customer_id:
        subs_qs = subs_qs.filter(customer_id=customer_id)

    active_subscriptions_count = subs_qs.filter(status='active').count()
    total_mrr = compute_mrr_for_active_subscriptions(plan_id=plan_id, customer_id=customer_id)
    total_arr = calculate_arr_from_mrr(total_mrr)

    # 2. Invoices & Outstanding queries
    today = datetime.date.today()
    invoices_qs = Invoice.objects.all()
    if customer_id:
        invoices_qs = invoices_qs.filter(customer_id=customer_id)
    if plan_id:
        invoices_qs = invoices_qs.filter(subscription__plan_id=plan_id)
    if start_date:
        invoices_qs = invoices_qs.filter(issue_date__gte=start_date)
    if end_date:
        invoices_qs = invoices_qs.filter(issue_date__lte=end_date)

    # Outstanding is sum of (total - amount_paid) over Confirmed invoices
    confirmed_invoices = invoices_qs.filter(status='confirmed')
    outstanding_agg = confirmed_invoices.aggregate(
        outstanding=Coalesce(Sum(F('total') - F('amount_paid')), Value(Decimal('0.00'), output_field=DecimalField()))
    )
    total_outstanding = outstanding_agg['outstanding'] or Decimal('0.00')

    # Overdue invoices: Confirmed, due_date < today, and amount_paid < total
    overdue_qs = confirmed_invoices.filter(due_date__lt=today, total__gt=F('amount_paid'))
    overdue_agg = overdue_qs.aggregate(
        count=Count('id'),
        amount=Coalesce(Sum(F('total') - F('amount_paid')), Value(Decimal('0.00'), output_field=DecimalField()))
    )
    overdue_count = overdue_agg['count'] or 0
    overdue_amount = overdue_agg['amount'] or Decimal('0.00')

    # 3. Revenue collected: sum of payments in the date range
    payments_qs = Payment.objects.all()
    if customer_id:
        payments_qs = payments_qs.filter(invoice__customer_id=customer_id)
    if plan_id:
        payments_qs = payments_qs.filter(invoice__subscription__plan_id=plan_id)
    if start_date:
        payments_qs = payments_qs.filter(payment_date__gte=start_date)
    if end_date:
        payments_qs = payments_qs.filter(payment_date__lte=end_date)

    payments_agg = payments_qs.aggregate(
        collected=Coalesce(Sum('amount'), Value(Decimal('0.00'), output_field=DecimalField()))
    )
    revenue_collected = payments_agg['collected'] or Decimal('0.00')

    result = {
        "active_subscriptions": active_subscriptions_count,
        "mrr": f"{total_mrr:.2f}",
        "arr": f"{total_arr:.2f}",
        "revenue_collected": f"{revenue_collected:.2f}",
        "total_outstanding": f"{total_outstanding:.2f}",
        "overdue_count": overdue_count,
        "overdue_amount": f"{overdue_amount:.2f}",
        "generated_at": datetime.datetime.now().isoformat()
    }

    if use_cache:
        cache.set(cache_key, result, timeout=60)

    return result


def get_active_subscriptions_report(
    plan_id: Optional[int] = None,
    customer_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Returns list of active subscriptions with calculated MRR per subscription.
    """
    qs = Subscription.objects.filter(status='active').select_related('customer', 'plan').prefetch_related('lines')
    if plan_id:
        qs = qs.filter(plan_id=plan_id)
    if customer_id:
        qs = qs.filter(customer_id=customer_id)

    data = []
    for sub in qs[:500]:
        lines_sum = sum((line.line_total for line in sub.lines.all()), Decimal('0.00'))
        sub_mrr = calculate_subscription_mrr(lines_sum, sub.plan.billing_period) if sub.plan else Decimal('0.00')
        data.append({
            "id": sub.id,
            "number": sub.number,
            "customer_id": sub.customer_id,
            "customer_email": sub.customer.email,
            "customer_name": getattr(sub.customer, 'name', '') or sub.customer.email,
            "plan_id": sub.plan_id,
            "plan_name": sub.plan.name if sub.plan else '',
            "billing_period": sub.plan.billing_period if sub.plan else '',
            "start_date": str(sub.start_date),
            "expiry_date": str(sub.expiry_date) if sub.expiry_date else None,
            "next_billing_date": str(sub.next_billing_date) if sub.next_billing_date else None,
            "status": sub.status,
            "is_paused": sub.is_paused,
            "recurring_total": f"{lines_sum:.2f}",
            "mrr": f"{sub_mrr:.2f}",
        })
    return data


def get_revenue_by_month(
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    plan_id: Optional[int] = None,
    customer_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Aggregates payments by month for revenue trends.
    Uses pure SQL TruncMonth and Coalesce.
    """
    qs = Payment.objects.all()
    if start_date:
        qs = qs.filter(payment_date__gte=start_date)
    if end_date:
        qs = qs.filter(payment_date__lte=end_date)
    if plan_id:
        qs = qs.filter(invoice__subscription__plan_id=plan_id)
    if customer_id:
        qs = qs.filter(invoice__customer_id=customer_id)

    monthly_data = (
        qs.annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('month')
    )

    return [
        {
            "month": item['month'].strftime('%Y-%m') if item['month'] else '',
            "revenue": f"{(item['total'] or Decimal('0.00')):.2f}",
            "payment_count": item['count']
        }
        for item in monthly_data
    ]


def get_overdue_invoices_report(
    plan_id: Optional[int] = None,
    customer_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Returns list of overdue invoices with days overdue and remaining balance.
    """
    today = datetime.date.today()
    qs = (
        Invoice.objects.filter(status='confirmed', due_date__lt=today, total__gt=F('amount_paid'))
        .select_related('customer', 'subscription')
        .order_by('due_date')
    )
    if plan_id:
        qs = qs.filter(subscription__plan_id=plan_id)
    if customer_id:
        qs = qs.filter(customer_id=customer_id)

    return [
        {
            "id": inv.id,
            "number": inv.number,
            "customer_id": inv.customer_id,
            "customer_email": inv.customer.email,
            "due_date": str(inv.due_date),
            "days_overdue": (today - inv.due_date).days,
            "total": f"{inv.total:.2f}",
            "amount_paid": f"{inv.amount_paid:.2f}",
            "balance": f"{(inv.total - inv.amount_paid):.2f}"
        }
        for inv in qs[:200]
    ]
