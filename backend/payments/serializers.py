from rest_framework import serializers
from payments.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.ReadOnlyField(source='invoice.number')
    recorded_by_email = serializers.ReadOnlyField(source='recorded_by.email')

    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_number', 'method', 'amount',
            'payment_date', 'note', 'recorded_by', 'recorded_by_email', 'created_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'recorded_by', 'recorded_by_email', 'created_at']
