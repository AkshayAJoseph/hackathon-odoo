from catalog.models import Tax

def resolve_tax(line):
    """
    Tax for a line: product tax, else default tax, else None (zero).
    Inactive taxes are ignored.
    """
    product = getattr(line, 'product', None)
    if product:
        product_tax = Tax.objects.filter(is_active=True, applies_to=product).first()
        if product_tax:
            return product_tax

    # Default tax (applies_to is None / not set)
    default_tax = Tax.objects.filter(is_active=True, applies_to__isnull=True).first()
    if default_tax:
        return default_tax

    return None
