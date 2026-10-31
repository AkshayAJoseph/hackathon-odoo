from django.db import models
from django.conf import settings
from decimal import Decimal
from plans.models import Plan
from catalog.models import Product, ProductVariant, Tax

class Subscription(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('quotation', 'Quotation'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    )

    number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    start_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    payment_terms = models.PositiveIntegerField(default=30) # days
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_paused = models.BooleanField(default=False)
    next_billing_date = models.DateField(null=True, blank=True)
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
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['customer']),
            models.Index(fields=['next_billing_date']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['status', 'customer']),
        ]

    def __str__(self):
        return f"{self.number} ({self.customer.email}) - {self.status}"

class SubscriptionLine(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='subscription_lines')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2) # Snapshotted at creation
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.subscription.number} - {self.product.name} x {self.quantity}"
