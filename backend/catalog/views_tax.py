from rest_framework import viewsets
from catalog.models import Tax
from catalog.serializers import TaxSerializer
from core.permissions import IsAdminOrReadOnlyStaff

class TaxViewSet(viewsets.ModelViewSet):
    queryset = Tax.objects.all().order_by('id')
    serializer_class = TaxSerializer
    permission_classes = [IsAdminOrReadOnlyStaff]
