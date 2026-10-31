from decimal import Decimal
from django.db import models


class Product(models.Model):
    TYPE_CHOICES = (
        ('service', 'Service'),
        ('software', 'Software'),
        ('addon', 'Addon'),
    )

    name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='software')
    sales_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    @property
    def type(self):
        return self.product_type

    @type.setter
    def type(self, value):
        self.product_type = value

    @property
    def margin(self):
        return self.sales_price - self.cost_price

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


class Tax(models.Model):
    TYPE_CHOICES = (
        ('percent', 'Percentage'),
        ('fixed', 'Fixed'),
    )

    name = models.CharField(max_length=100)
    rate_percent = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='percent')
    is_active = models.BooleanField(default=True)
    applies_to = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taxes'
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Taxes'

    @property
    def rate(self):
        return self.rate_percent

    @rate.setter
    def rate(self, val):
        self.rate_percent = val

    def __str__(self):
        scope = f" (Product: {self.applies_to.name})" if self.applies_to else " (All products)"
        return f"{self.name} - {self.rate_percent}%{scope}"
