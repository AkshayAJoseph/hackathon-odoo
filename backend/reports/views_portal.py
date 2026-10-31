from rest_framework import viewsets, permissions
from subscriptions.models import Subscription
from billing.models import Invoice
from billing.serializers import InvoiceSerializer
from reports.serializers_portal import PortalSubscriptionSerializer

class PortalSubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer portal API for subscriptions.
    Strictly scoped to request.user - customers cannot view other customer records.
    """
    serializer_class = PortalSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Subscription.objects.filter(customer=user)
            .select_related('plan')
            .prefetch_related('lines__product', 'lines__variant')
            .order_by('-id')
        )

class PortalInvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer portal API for invoices.
    Strictly scoped to request.user - customers cannot view other customer records (404 on foreign ID).
    """
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Invoice.objects.filter(customer=user)
            .select_related('customer', 'subscription')
            .prefetch_related('lines')
            .order_by('-id')
        )

