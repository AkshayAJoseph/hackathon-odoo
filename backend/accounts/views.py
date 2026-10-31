from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.serializers import (
    SignupSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    StaffCreateSerializer,
)
from accounts.models import User
from accounts.services import request_password_reset, reset_password, create_staff
from core.permissions import IsAdmin, IsStaffOrAdmin
from core.pagination import StandardPagination

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            request_password_reset(serializer.validated_data['email'])
            return Response({
                "message": "If an account with that email exists, a password reset link has been sent."
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                reset_password(
                    uid=serializer.validated_data['uid'],
                    token=serializer.validated_data['token'],
                    new_password=serializer.validated_data['new_password']
                )
                return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsStaffOrAdmin()]

    def get(self, request):
        staff_qs = User.objects.filter(role__in=['staff', 'admin']).order_by('-date_joined')
        paginator = StandardPagination()
        page = paginator.paginate_queryset(staff_qs, request)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = UserSerializer(staff_qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StaffCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = create_staff(request.user, serializer.validated_data)
                return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
