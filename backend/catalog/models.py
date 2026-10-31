from django.db import models
from decimal import Decimal

class Product(models.Model):
    TYPE_CHOICES = (
        ('service', 'Service'),
        ('software', 'Software'),
        ('addon', 'Addon'),
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='software')
    sales_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def margin(self):
        return self.sales_price - self.cost_price

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    attribute = models.CharField(max_length=100) # e.g. 'Brand'
    value = models.CharField(max_length=100)     # e.g. 'Odoo'
    extra_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.product.name} - {self.attribute}: {self.value} (+{self.extra_price})"

    @property
    def effective_price(self):
        return self.product.sales_price + self.extra_price

class Tax(models.Model):
    TYPE_CHOICES = (
        ('percent', 'Percentage'),
        ('fixed', 'Fixed'),
    )
    name = models.CharField(max_length=100)
    rate_percent = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='percent')
    is_active = models.BooleanField(default=True)
    applies_to = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='taxes')

    class Meta:
        verbose_name_plural = 'Taxes'

    def __str__(self):
        scope = f" (Product: {self.applies_to.name})" if self.applies_to else " (All products)"
        return f"{self.name} - {self.rate_percent}%{scope}"
