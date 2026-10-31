from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from discounts.models import Discount

TWOPLACES = Decimal('0.01')

def quantize_money(val):
    if val is None:
        val = Decimal('0.00')
    if not isinstance(val, Decimal):
        val = Decimal(str(val))
    return val.quantize(TWOPLACES, rounding=ROUND_HALF_UP)

def find_eligible_discounts(subscription, as_of=None):
    """
    Finds all active discounts that qualify for the given subscription as of a date.
    Checks:
    - is_active = True
    - date between start_date and end_date (inclusive, if set)
    - times_used < usage_limit (if limit set)
    - min_purchase <= subtotal (if set)
    - min_quantity <= total quantity (if set)
    - scope matches products on subscription
    """
    if as_of is None:
        as_of = date.today()

    lines = list(subscription.lines.all())
    subtotal = sum((line.quantity * line.unit_price for line in lines), Decimal('0.00'))
    total_qty = sum((line.quantity for line in lines), 0)

    # Base query
    candidates = Discount.objects.filter(is_active=True)
    eligible = []

    for d in candidates:
        if d.start_date and d.start_date > as_of:
            continue
        if d.end_date and d.end_date < as_of:
            continue
        if d.usage_limit is not None and d.times_used >= d.usage_limit:
            continue

        if d.scope == 'product':
            matching_lines = [l for l in lines if l.product_id == d.product_id]
            if not matching_lines:
                continue
            prod_subtotal = sum((l.quantity * l.unit_price for l in matching_lines), Decimal('0.00'))
            prod_qty = sum((l.quantity for l in matching_lines), 0)
            if d.min_purchase and prod_subtotal < d.min_purchase:
                continue
            if d.min_quantity and prod_qty < d.min_quantity:
                continue
        else:
            if d.min_purchase and subtotal < d.min_purchase:
                continue
            if d.min_quantity and total_qty < d.min_quantity:
                continue

        eligible.append(d)

    return eligible

def calculate_discount_savings(d, lines):
    """
    Computes (savings_map, total_savings) for a given discount across lines.
    savings_map: dict of {line.id: discount_for_this_line}
    """
    savings_map = {line.id: Decimal('0.00') for line in lines}
    total_savings = Decimal('0.00')

    if d.scope == 'product':
        matching_lines = [l for l in lines if l.product_id == d.product_id]
        if not matching_lines:
            return savings_map, Decimal('0.00')

        if d.kind == 'percent':
            for line in matching_lines:
                gross = quantize_money(line.quantity * line.unit_price)
                disc = quantize_money(gross * (d.value / Decimal('100')))
                disc = min(disc, gross)
                savings_map[line.id] = disc
                total_savings += disc
        elif d.kind == 'fixed':
            remaining_fixed = quantize_money(d.value)
            for line in matching_lines:
                if remaining_fixed <= Decimal('0.00'):
                    break
                gross = quantize_money(line.quantity * line.unit_price)
                alloc = min(remaining_fixed, gross)
                savings_map[line.id] = alloc
                total_savings += alloc
                remaining_fixed -= alloc
    else: # subscription scope
        subtotal = sum((quantize_money(line.quantity * line.unit_price) for line in lines), Decimal('0.00'))
        if d.kind == 'percent':
            for line in lines:
                gross = quantize_money(line.quantity * line.unit_price)
                disc = quantize_money(gross * (d.value / Decimal('100')))
                disc = min(disc, gross)
                savings_map[line.id] = disc
                total_savings += disc
        elif d.kind == 'fixed':
            remaining_fixed = quantize_money(d.value)
            for line in lines:
                if remaining_fixed <= Decimal('0.00'):
                    break
                gross = quantize_money(line.quantity * line.unit_price)
                alloc = min(remaining_fixed, gross)
                savings_map[line.id] = alloc
                total_savings += alloc
                remaining_fixed -= alloc

    return savings_map, quantize_money(total_savings)

def apply_discounts(subscription, lines=None, as_of=None):
    """
    Picks the best eligible discount per scope and returns {line_id: discount_amount}.
    """
    if as_of is None:
        as_of = date.today()
    if lines is None:
        lines = list(subscription.lines.all())

    eligible = find_eligible_discounts(subscription, as_of=as_of)
    if not eligible:
        return {line.id: Decimal('0.00') for line in lines}

    best_discount = None
    best_savings = Decimal('0.00')
    best_map = {line.id: Decimal('0.00') for line in lines}

    for d in eligible:
        savings_map, total = calculate_discount_savings(d, lines)
        if total > best_savings:
            best_savings = total
            best_discount = d
            best_map = savings_map

    return best_map

def get_best_eligible_discount(subscription, lines=None, as_of=None):
    """
    Returns (best_discount, line_discounts_map, total_discount_amount)
    """
    if as_of is None:
        as_of = date.today()
    if lines is None:
        lines = list(subscription.lines.all())

    eligible = find_eligible_discounts(subscription, as_of=as_of)
    if not eligible:
        return None, {line.id: Decimal('0.00') for line in lines}, Decimal('0.00')

    best_discount = None
    best_savings = Decimal('0.00')
    best_map = {line.id: Decimal('0.00') for line in lines}

    for d in eligible:
        savings_map, total = calculate_discount_savings(d, lines)
        if total > best_savings:
            best_savings = total
            best_discount = d
            best_map = savings_map

    return best_discount, best_map, best_savings
