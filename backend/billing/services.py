from decimal import Decimal, ROUND_HALF_UP

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
    Returns dict:
        {
            'quantity': qty,
            'unit_price': unit_price,
            'discount': discount,
            'net': line_net,
            'tax_rate': tax_rate,
            'tax': tax_amount,
            'total': line_total,
        }
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
