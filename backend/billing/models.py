from django.db import models
from django.conf import settings
from decimal import Decimal
from datetime import date
from subscriptions.models import Subscription
from catalog.models import Product

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )

    number = models.CharField(max_length=50, unique=True, db_index=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.PROTECT, related_name='invoices')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='invoices')
    period_start = models.DateField()
    period_end = models.DateField()
    issue_date = models.DateField(default=date.today)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subscription', 'period_start'],
                name='unique_subscription_period_start'
            )
        ]
        indexes = [
            models.Index(fields=['status', 'due_date', 'customer']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['customer']),
            models.Index(fields=['subscription']),
        ]

    def __str__(self):
        return f"{self.number} ({self.customer.email}) - {self.total} [{self.status}]"

    @property
    def balance(self):
        return max(Decimal('0.00'), self.total - self.amount_paid)

    def is_overdue(self, today=None):
        if today is None:
            today = date.today()
        return bool(self.status == 'confirmed' and self.due_date < today and self.balance > Decimal('0.00'))

    def days_overdue(self, today=None):
        if today is None:
            today = date.today()
        if self.is_overdue(today):
            return (today - self.due_date).days
        return 0

class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice_lines')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_rate = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.invoice.number}: {self.description} - {self.line_total}"
