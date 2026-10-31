from django.contrib import admin
from django.urls import path, include
from core.views import HealthCheckView
from accounts.views import StaffListCreateView
from plans.views import QuotationTemplateListCreateView, QuotationTemplateDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health', HealthCheckView.as_view(), name='health-check'),
    path('api/health/', HealthCheckView.as_view(), name='health-check-slash'),
    path('api/auth/', include('accounts.urls')),
    path('api/staff', StaffListCreateView.as_view(), name='staff-list-create'),
    path('api/staff/', StaffListCreateView.as_view(), name='staff-list-create-slash'),
    path('api/products/', include('catalog.urls')),
    path('api/products', include('catalog.urls')),
    path('api/plans/', include('plans.urls')),
    path('api/plans', include('plans.urls')),
    path('api/quotation-templates', QuotationTemplateListCreateView.as_view(), name='quotation-template-list-create'),
    path('api/quotation-templates/', QuotationTemplateListCreateView.as_view(), name='quotation-template-list-create-slash'),
    path('api/quotation-templates/<int:pk>', QuotationTemplateDetailView.as_view(), name='quotation-template-detail'),
    path('api/quotation-templates/<int:pk>/', QuotationTemplateDetailView.as_view(), name='quotation-template-detail-slash'),
    path('api/taxes/', include('catalog.urls_tax')),
    path('api/discounts/', include('discounts.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/invoices/', include('billing.urls_invoice')),
    path('api/payments/', include('payments.urls')),
]
