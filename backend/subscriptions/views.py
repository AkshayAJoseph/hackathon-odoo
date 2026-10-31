from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound
from django.shortcuts import get_object_or_404

from core.permissions import IsStaffOrAdmin
from core.services import scoped_queryset
from accounts.models import User
from plans.models import QuotationTemplate
from subscriptions.models import Subscription
from subscriptions.serializers import SubscriptionSerializer
from subscriptions.services import (
    generate_subscription_number,
    create_from_template,
    send_quote,
    confirm,
    activate,
    close_subscription,
    pause,
    resume,
    renew,
)


class SubscriptionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        qs = Subscription.objects.select_related('customer', 'plan').prefetch_related('lines__product', 'lines__variant')
        return scoped_queryset(self.request.user, qs)

    def perform_create(self, serializer):
        sub_number = generate_subscription_number()
        serializer.save(
            number=sub_number,
            status='draft',
            created_by=self.request.user
        )


class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        qs = Subscription.objects.select_related('customer', 'plan').prefetch_related('lines__product', 'lines__variant')
        return scoped_queryset(self.request.user, qs)


class CreateSubscriptionFromTemplateView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def post(self, request, pk=None):
        template = get_object_or_404(QuotationTemplate.objects.prefetch_related('lines'), pk=pk)
        customer_id = request.data.get('customer')
        if not customer_id:
            raise ValidationError({"customer": ["Customer ID is required."]})

        customer = get_object_or_404(User, pk=customer_id)
        quote_date = request.data.get('quote_date', None)

        sub = create_from_template(
            template=template,
            customer=customer,
            user=request.user,
            quote_date=quote_date
        )

        serializer = SubscriptionSerializer(sub)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BaseSubscriptionActionView(APIView):
    permission_classes = [IsAuthenticated]

    def get_subscription(self, request, pk):
        qs = Subscription.objects.select_related('customer', 'plan').prefetch_related('lines__product', 'lines__variant')
        scoped = scoped_queryset(request.user, qs)
        return get_object_or_404(scoped, pk=pk)


class SendQuoteView(BaseSubscriptionActionView):
    def post(self, request, pk=None):
        sub = self.get_subscription(request, pk)
        sub = send_quote(sub, request.user)
        return Response(SubscriptionSerializer(sub).data, status=status.HTTP_200_OK)


class ConfirmSubscriptionView(BaseSubscriptionActionView):
    def post(self, request, pk=None):
        sub = self.get_subscription(request, pk)
        sub = confirm(sub, request.user)
        return Response(SubscriptionSerializer(sub).data, status=status.HTTP_200_OK)


class ActivateSubscriptionView(BaseSubscriptionActionView):
    def post(self, request, pk=None):
        sub = self.get_subscription(request, pk)
        sub = activate(sub, request.user)
        return Response(SubscriptionSerializer(sub).data, status=status.HTTP_200_OK)


class CloseSubscriptionView(BaseSubscriptionActionView):
    def post(self, request, pk=None):
        sub = self.get_subscription(request, pk)
        sub = close_subscription(sub, request.user)
        return Response(SubscriptionSerializer(sub).data, status=status.HTTP_200_OK)


class PauseSubscriptionView(BaseSubscriptionActionView):
    def post(self, request, pk=None):
        sub = self.get_subscription(request, pk)
        sub = pause(sub, request.user)
        return Response(SubscriptionSerializer(sub).data, status=status.HTTP_200_OK)


class ResumeSubscriptionView(BaseSubscriptionActionView):
    def post(self, request, pk=None):
        sub = self.get_subscription(request, pk)
        sub = resume(sub, request.user)
        return Response(SubscriptionSerializer(sub).data, status=status.HTTP_200_OK)


class RenewSubscriptionView(BaseSubscriptionActionView):
    def post(self, request, pk=None):
        sub = self.get_subscription(request, pk)
        sub = renew(sub, request.user)
        return Response(SubscriptionSerializer(sub).data, status=status.HTTP_200_OK)
