from django.contrib import admin
from django.urls import path, include
from core.views import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health', HealthCheckView.as_view(), name='health-check'),
    path('api/health/', HealthCheckView.as_view(), name='health-check-slash'),
    path('api/taxes/', include('catalog.urls_tax')),
    path('api/discounts/', include('discounts.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/invoices/', include('billing.urls_invoice')),
    path('api/payments/', include('payments.urls')),
    path('api/reports/', include('reports.urls')),
]
