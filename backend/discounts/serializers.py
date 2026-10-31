from rest_framework import serializers
from discounts.models import Discount, DiscountUsage

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = [
            'id', 'name', 'kind', 'value', 'min_purchase', 'min_quantity',
            'start_date', 'end_date', 'usage_limit', 'times_used',
            'scope', 'product', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class DiscountUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountUsage
        fields = ['id', 'discount', 'invoice', 'subscription', 'amount', 'created_at']
        read_only_fields = ['id', 'created_at']
