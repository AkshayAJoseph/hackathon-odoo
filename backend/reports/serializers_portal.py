from rest_framework import serializers
from subscriptions.models import Subscription, SubscriptionLine
from plans.models import Plan
from catalog.models import Product, ProductVariant

class SubscriptionLineSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='variant.value', read_only=True, allow_null=True)

    class Meta:
        model = SubscriptionLine
        fields = [
            'id', 'product', 'product_name', 'variant', 'variant_name',
            'quantity', 'unit_price', 'tax', 'discount_amount', 'line_total'
        ]

class PortalSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    billing_period = serializers.CharField(source='plan.billing_period', read_only=True)
    lines = SubscriptionLineSerializer(many=True, read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'number', 'plan', 'plan_name', 'billing_period',
            'start_date', 'expiry_date', 'payment_terms', 'status',
            'is_paused', 'next_billing_date', 'created_at', 'lines'
        ]

