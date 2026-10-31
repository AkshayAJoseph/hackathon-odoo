from django.urls import path
from billing.views import run_billing_view

urlpatterns = [
    path('run/', run_billing_view, name='billing-run'),
]
