from rest_framework import serializers
from decimal import Decimal
from datetime import date
from billing.models import Invoice, InvoiceLine

class InvoiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLine
        fields = [
            'id', 'product', 'description', 'quantity', 'unit_price',
            'discount', 'tax_rate', 'tax_amount', 'line_total'
        ]

class InvoiceSerializer(serializers.ModelSerializer):
    customer_email = serializers.ReadOnlyField(source='customer.email')
    subscription_number = serializers.ReadOnlyField(source='subscription.number')
    balance = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()
    lines = InvoiceLineSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'number', 'customer', 'customer_email', 'subscription', 'subscription_number',
            'period_start', 'period_end', 'issue_date', 'due_date', 'status',
            'subtotal', 'discount_total', 'tax_total', 'total', 'amount_paid',
            'balance', 'is_overdue', 'days_overdue', 'sent_at', 'lines', 'created_at'
        ]
        read_only_fields = fields

    def get_balance(self, obj):
        return str(obj.balance)

    def get_is_overdue(self, obj):
        return obj.is_overdue()

    def get_days_overdue(self, obj):
        return obj.days_overdue()
