from rest_framework import viewsets
from discounts.models import Discount, DiscountUsage
from discounts.serializers import DiscountSerializer, DiscountUsageSerializer
from core.permissions import IsAdmin

class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all().order_by('-id')
    serializer_class = DiscountSerializer
    permission_classes = [IsAdmin]

class DiscountUsageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DiscountUsage.objects.all().order_by('-created_at')
    serializer_class = DiscountUsageSerializer
    permission_classes = [IsAdmin]
