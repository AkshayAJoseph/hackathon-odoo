from django.urls import path
from accounts.views import (
    SignupView,
    CustomTokenObtainPairView,
    MeView,
    ForgotPasswordView,
    ResetPasswordView,
)

urlpatterns = [
    path('signup', SignupView.as_view(), name='auth-signup'),
    path('signup/', SignupView.as_view(), name='auth-signup-slash'),
    path('login', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth-login-slash'),
    path('me', MeView.as_view(), name='auth-me'),
    path('me/', MeView.as_view(), name='auth-me-slash'),
    path('forgot', ForgotPasswordView.as_view(), name='auth-forgot'),
    path('forgot/', ForgotPasswordView.as_view(), name='auth-forgot-slash'),
    path('reset', ResetPasswordView.as_view(), name='auth-reset'),
    path('reset/', ResetPasswordView.as_view(), name='auth-reset-slash'),
]
