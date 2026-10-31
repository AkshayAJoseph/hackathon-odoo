from rest_framework import serializers
from catalog.models import Tax, Product, ProductVariant

class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ['id', 'name', 'rate_percent', 'type', 'is_active', 'applies_to']


class ProductVariantSerializer(serializers.ModelSerializer):
    extra_price = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=True)
    effective_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, coerce_to_string=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'attribute', 'value', 'extra_price', 'effective_price']
        read_only_fields = ['id', 'product', 'effective_price']


class ProductSerializer(serializers.ModelSerializer):
    sales_price = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=True)
    cost_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, coerce_to_string=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'product_type', 'sales_price', 'cost_price', 'notes', 'is_active', 'variants', 'created_at', 'updated_at']
        read_only_fields = ['id', 'variants', 'created_at', 'updated_at']
