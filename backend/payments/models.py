from django.db import models
from django.conf import settings
from decimal import Decimal
from datetime import date
from billing.models import Invoice

class Payment(models.Model):
    METHOD_CHOICES = (
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
    )

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=30, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payment_date = models.DateField(default=date.today)
    note = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['invoice', 'payment_date']),
            models.Index(fields=['invoice']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['method']),
        ]

    def __str__(self):
        return f"Payment {self.id}: {self.amount} ({self.method}) for {self.invoice.number}"
