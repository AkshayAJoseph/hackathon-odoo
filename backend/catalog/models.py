from decimal import Decimal
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=50)
    sales_price = models.DecimalField(max_digits=12, decimal_places=2)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (${self.sales_price})"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    attribute = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    extra_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['product', 'attribute', 'value']
        unique_together = ('product', 'attribute', 'value')

    @property
    def effective_price(self) -> Decimal:
        return self.product.sales_price + self.extra_price

    def __str__(self):
        sign = "+" if self.extra_price >= Decimal('0.00') else ""
        return f"{self.product.name} - {self.attribute}: {self.value} ({sign}{self.extra_price})"


# Minimal Tax model stub so lazy relation 'catalog.Tax' resolves cleanly
# Amrutha owns Tax business logic, rate rules, and calculation engines.
class Tax(models.Model):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.rate}%)"

