from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'app': 'brightloop-backend'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/taxes/', include('catalog.urls_tax')),
    path('api/discounts/', include('discounts.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/invoices/', include('billing.urls_invoice')),
    path('api/payments/', include('payments.urls')),
]
