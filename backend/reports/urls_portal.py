from django.urls import path, include
from rest_framework.routers import DefaultRouter
from reports.views_portal import PortalSubscriptionViewSet, PortalInvoiceViewSet

router = DefaultRouter()
router.register(r'subscriptions', PortalSubscriptionViewSet, basename='portal-subscription')
router.register(r'invoices', PortalInvoiceViewSet, basename='portal-invoice')

urlpatterns = [
    path('', include(router.urls)),
]

