from rest_framework import generics
from core.permissions import IsAdminOrReadOnlyStaff, IsStaffOrAdmin
from plans.models import Plan, QuotationTemplate, TemplateLine
from plans.serializers import PlanSerializer, QuotationTemplateSerializer


class PlanListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnlyStaff]
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class PlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnlyStaff]
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class QuotationTemplateListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaffOrAdmin]
    queryset = QuotationTemplate.objects.select_related('plan').prefetch_related('lines__product', 'lines__variant').all()
    serializer_class = QuotationTemplateSerializer


class QuotationTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffOrAdmin]
    queryset = QuotationTemplate.objects.select_related('plan').prefetch_related('lines__product', 'lines__variant').all()
    serializer_class = QuotationTemplateSerializer
