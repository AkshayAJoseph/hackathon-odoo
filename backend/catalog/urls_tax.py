from django.urls import path, include
from rest_framework.routers import DefaultRouter
from catalog.views_tax import TaxViewSet

router = DefaultRouter()
router.register(r'', TaxViewSet, basename='tax')

urlpatterns = [
    path('', include(router.urls)),
]
