from django.db import models
from decimal import Decimal
from catalog.models import Product

class Discount(models.Model):
    KIND_CHOICES = (
        ('fixed', 'Fixed Amount'),
        ('percent', 'Percentage'),
    )
    SCOPE_CHOICES = (
        ('product', 'Product'),
        ('subscription', 'Subscription'),
    )

    name = models.CharField(max_length=255)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='percent')
    value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    min_purchase = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    min_quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    times_used = models.PositiveIntegerField(default=0)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='subscription')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='discounts')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        symbol = "%" if self.kind == 'percent' else " USD"
        return f"{self.name} ({self.value}{symbol} - {self.scope})"

class DiscountUsage(models.Model):
    discount = models.ForeignKey(Discount, on_delete=models.PROTECT, related_name='usages')
    invoice = models.ForeignKey('billing.Invoice', on_delete=models.CASCADE, related_name='discount_usages')
    subscription = models.ForeignKey('subscriptions.Subscription', on_delete=models.SET_NULL, null=True, blank=True, related_name='discount_usages')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.discount.name} on Invoice {self.invoice_id} ({self.amount})"
