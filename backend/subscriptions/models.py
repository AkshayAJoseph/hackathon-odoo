from decimal import Decimal
from django.db import models
from django.conf import settings


class Subscription(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('quotation', 'Quotation'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    )

    number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        db_index=True
    )
    plan = models.ForeignKey('plans.Plan', on_delete=models.PROTECT, related_name='subscriptions')
    start_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    payment_terms = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    is_paused = models.BooleanField(default=False, db_index=True)
    next_billing_date = models.DateField(null=True, blank=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_subscriptions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['customer']),
            models.Index(fields=['next_billing_date']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['status', 'customer']),
            models.Index(fields=['status', 'customer', 'next_billing_date', 'expiry_date']),
            models.Index(fields=['status', 'is_paused', 'next_billing_date']),
        ]

    def __str__(self):
        return f"{self.number} ({self.customer.email}) - {self.status}"


class SubscriptionLine(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT, related_name='subscription_lines')
    variant = models.ForeignKey('catalog.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)  # Snapshotted at creation
    tax = models.ForeignKey('catalog.Tax', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['id']

    @property
    def subtotal(self) -> Decimal:
        return Decimal(self.quantity) * self.unit_price

    def __str__(self):
        return f"{self.subscription.number} - {self.product.name} x {self.quantity}"
