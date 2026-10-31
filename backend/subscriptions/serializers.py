from rest_framework import serializers
from decimal import Decimal
from subscriptions.models import Subscription, SubscriptionLine
from accounts.models import User
from plans.models import Plan


class SubscriptionLineSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=True)
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=True, default=Decimal('0.00'))
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=True, default=Decimal('0.00'))
    subtotal = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionLine
        fields = [
            'id',
            'product',
            'product_name',
            'variant',
            'variant_name',
            'quantity',
            'unit_price',
            'tax',
            'discount_amount',
            'line_total',
            'subtotal',
        ]

    def get_subtotal(self, obj) -> str:
        return f"{obj.subtotal:.2f}"

    def get_variant_name(self, obj):
        if not obj.variant:
            return None
        return f"{obj.variant.attribute}: {obj.variant.value}"


class SubscriptionSerializer(serializers.ModelSerializer):
    lines = SubscriptionLineSerializer(many=True, read_only=True)
    allowed_actions = serializers.SerializerMethodField()
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id',
            'number',
            'customer',
            'customer_name',
            'customer_email',
            'plan',
            'plan_name',
            'start_date',
            'expiry_date',
            'payment_terms',
            'status',
            'is_paused',
            'next_billing_date',
            'created_by',
            'lines',
            'total_amount',
            'allowed_actions',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'number',
            'customer_name',
            'customer_email',
            'plan_name',
            'total_amount',
            'status',
            'is_paused',
            'next_billing_date',
            'created_by',
            'created_at',
            'updated_at',
            'allowed_actions',
        ]

    def get_total_amount(self, obj) -> str:
        total = sum((l.line_total for l in obj.lines.all()), Decimal('0.00'))
        return f"{total:.2f}"

    def get_allowed_actions(self, obj) -> list[str]:
        """
        Computes valid next actions based on current status and plan capabilities:
        - draft: ['send_quote']
        - quotation: ['confirm']
        - confirmed: ['activate']
        - active:
            - 'pause' (if plan.pausable and not paused) / 'resume' (if plan.pausable and paused)
            - 'close' (if plan.closable)
            - 'renew' (if plan.renewable)
        - closed: []
        """
        actions = []
        if obj.status == 'draft':
            actions.append('send_quote')
        elif obj.status == 'quotation':
            actions.append('confirm')
        elif obj.status == 'confirmed':
            actions.append('activate')
        elif obj.status == 'active':
            if obj.plan.pausable:
                if obj.is_paused:
                    actions.append('resume')
                else:
                    actions.append('pause')
            if obj.plan.closable:
                actions.append('close')
            if obj.plan.renewable:
                actions.append('renew')
        elif obj.status == 'closed':
            pass

        return actions
