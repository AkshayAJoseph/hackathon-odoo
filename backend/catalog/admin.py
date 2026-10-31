from django.contrib import admin
from catalog.models import Product, ProductVariant, Tax

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'sales_price', 'cost_price', 'margin', 'is_active')
    list_filter = ('product_type', 'is_active')
    search_fields = ('name',)
    inlines = [ProductVariantInline]

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'attribute', 'value', 'extra_price', 'effective_price')
    list_filter = ('attribute', 'product')
    search_fields = ('product__name', 'attribute', 'value')

@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate_percent', 'type', 'applies_to', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name',)
