from decimal import Decimal
import pytest
from reports.services import calculate_subscription_mrr, calculate_arr_from_mrr

def test_monthly_mrr_calculation():
    # Monthly: exactly equal to the monthly recurring fee
    fee = Decimal('100.00')
    mrr = calculate_subscription_mrr(fee, 'monthly')
    assert mrr == Decimal('100.00')
    assert calculate_arr_from_mrr(mrr) == Decimal('1200.00')

def test_yearly_mrr_calculation():
    # Yearly: divided by 12
    # 1200 / 12 = 100.00
    fee = Decimal('1200.00')
    mrr = calculate_subscription_mrr(fee, 'yearly')
    assert mrr == Decimal('100.00')
    assert calculate_arr_from_mrr(mrr) == Decimal('1200.00')

    # Non-divisible yearly amount: 1000 / 12 = 83.3333... -> 83.33
    fee_odd = Decimal('1000.00')
    mrr_odd = calculate_subscription_mrr(fee_odd, 'yearly')
    assert mrr_odd == Decimal('83.33')
    assert calculate_arr_from_mrr(mrr_odd) == Decimal('999.96')

def test_weekly_mrr_calculation():
    # Weekly: weekly * 52 / 12
    # 100 * 52 / 12 = 5200 / 12 = 433.3333... -> 433.33
    fee = Decimal('100.00')
    mrr = calculate_subscription_mrr(fee, 'weekly')
    assert mrr == Decimal('433.33')

def test_daily_mrr_calculation():
    # Daily: daily * 365 / 12
    # 10 * 365 / 12 = 3650 / 12 = 304.1666... -> 304.17 (ROUND_HALF_UP)
    fee = Decimal('10.00')
    mrr = calculate_subscription_mrr(fee, 'daily')
    assert mrr == Decimal('304.17')

def test_zero_and_negative_amounts():
    assert calculate_subscription_mrr(Decimal('0.00'), 'monthly') == Decimal('0.00')
    assert calculate_subscription_mrr(Decimal('-50.00'), 'monthly') == Decimal('0.00')

def test_unsupported_period():
    with pytest.raises(ValueError):
        calculate_subscription_mrr(Decimal('100.00'), 'quarterly')

