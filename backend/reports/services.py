import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional

# Billing period normalisation factors to convert recurring fees into Monthly Recurring Revenue (MRR)
# Daily: 365 days / 12 months
DAILY_FACTOR = Decimal('365') / Decimal('12')
# Weekly: 52 weeks / 12 months
WEEKLY_FACTOR = Decimal('52') / Decimal('12')
# Monthly: 1 month
MONTHLY_FACTOR = Decimal('1')
# Yearly: 1/12 month
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
    """
    ARR is MRR multiplied by 12.
    """
    if mrr is None:
        return Decimal('0.00')
    arr = mrr * Decimal('12')
    return arr.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def get_dashboard_summary(
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    plan_id: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Stub for the dashboard reporting aggregation service.
    In Hour 2, this will be connected to ORM aggregate() queries with PostgreSQL indexes.
    All monetary figures are returned formatted as exact strings to prevent floating-point drift.
    """
    return {
        "active_subscriptions": 0,
        "mrr": "0.00",
        "arr": "0.00",
        "revenue_collected": "0.00",
        "total_outstanding": "0.00",
        "overdue_count": 0,
        "overdue_amount": "0.00"
    }


def get_revenue_by_month(year: Optional[int] = None) -> list:
    """
    Stub for monthly revenue trends across the trailing 12 months.
    """
    return []


def get_overdue_invoices_report() -> list:
    """
    Stub for overdue invoice chasing list.
    """
    return []

