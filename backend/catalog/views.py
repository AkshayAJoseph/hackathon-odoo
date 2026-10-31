from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core.permissions import IsAdminOrReadOnlyStaff
from catalog.models import Product, ProductVariant
from catalog.serializers import ProductSerializer, ProductVariantSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnlyStaff]
    queryset = Product.objects.prefetch_related('variants').all()
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnlyStaff]
    queryset = Product.objects.prefetch_related('variants').all()
    serializer_class = ProductSerializer


class ProductVariantListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnlyStaff]
    serializer_class = ProductVariantSerializer

    def get_queryset(self):
        return ProductVariant.objects.filter(product_id=self.kwargs['product_id'])

    def perform_create(self, serializer):
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        serializer.save(product=product)


class ProductVariantDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnlyStaff]
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
