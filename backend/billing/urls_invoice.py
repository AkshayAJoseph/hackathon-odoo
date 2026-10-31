from django.urls import path, include
from rest_framework.routers import DefaultRouter
from billing.views_invoice import InvoiceViewSet

router = DefaultRouter()
router.register(r'', InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('', include(router.urls)),
]
