from django.urls import path, include
from rest_framework.routers import DefaultRouter
from discounts.views import DiscountViewSet, DiscountUsageViewSet

router = DefaultRouter()
router.register(r'usages', DiscountUsageViewSet, basename='discount-usage')
router.register(r'', DiscountViewSet, basename='discount')

urlpatterns = [
    path('', include(router.urls)),
]
