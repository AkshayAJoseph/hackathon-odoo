from django.urls import path
from catalog.views import (
    ProductListCreateView,
    ProductDetailView,
    ProductVariantListCreateView,
    ProductVariantDetailView,
)

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail-slash'),
    path('<int:product_id>/variants', ProductVariantListCreateView.as_view(), name='product-variant-list-create'),
    path('<int:product_id>/variants/', ProductVariantListCreateView.as_view(), name='product-variant-list-create-slash'),
    path('<int:product_id>/variants/<int:pk>', ProductVariantDetailView.as_view(), name='product-variant-detail'),
    path('<int:product_id>/variants/<int:pk>/', ProductVariantDetailView.as_view(), name='product-variant-detail-slash'),
]
