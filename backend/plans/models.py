from django.db import models
from decimal import Decimal
from catalog.models import Product, ProductVariant

class Plan(models.Model):
    PERIOD_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    billing_period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')
    min_quantity = models.PositiveIntegerField(default=1)
    available_from = models.DateField(null=True, blank=True)
    available_to = models.DateField(null=True, blank=True)

    # Per-plan admin flags
    auto_close = models.BooleanField(default=False)
    closable = models.BooleanField(default=True)
    pausable = models.BooleanField(default=True)
    renewable = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.billing_period})"

class QuotationTemplate(models.Model):
    name = models.CharField(max_length=255)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='templates')
    validity_days = models.PositiveIntegerField(default=30)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name

class TemplateLine(models.Model):
    template = models.ForeignKey(QuotationTemplate, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='template_lines')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, related_name='template_lines')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
