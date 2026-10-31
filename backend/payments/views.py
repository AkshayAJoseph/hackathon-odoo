from rest_framework import viewsets, permissions
from core.permissions import IsStaffOrAdmin
from payments.models import Payment
from payments.serializers import PaymentSerializer

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related('invoice', 'recorded_by').order_by('-payment_date', '-id')

        if user.role == 'customer':
            qs = qs.filter(invoice__customer=user)

        method = self.request.query_params.get('method')
        if method:
            qs = qs.filter(method=method)

        invoice_param = self.request.query_params.get('invoice')
        if invoice_param:
            if invoice_param.isdigit():
                qs = qs.filter(invoice_id=invoice_param)
            else:
                qs = qs.filter(invoice__number=invoice_param)

        start_date = self.request.query_params.get('start_date')
        if start_date:
            qs = qs.filter(payment_date__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            qs = qs.filter(payment_date__lte=end_date)

        return qs
