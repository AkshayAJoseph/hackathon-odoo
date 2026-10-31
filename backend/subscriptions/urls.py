from django.urls import path
from subscriptions.views import (
    SubscriptionListCreateView,
    SubscriptionDetailView,
    SendQuoteView,
    ConfirmSubscriptionView,
    ActivateSubscriptionView,
    CloseSubscriptionView,
    PauseSubscriptionView,
    ResumeSubscriptionView,
    RenewSubscriptionView,
)

urlpatterns = [
    path('', SubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('<int:pk>', SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail-slash'),
    path('<int:pk>/send-quote', SendQuoteView.as_view(), name='subscription-send-quote'),
    path('<int:pk>/send-quote/', SendQuoteView.as_view(), name='subscription-send-quote-slash'),
    path('<int:pk>/confirm', ConfirmSubscriptionView.as_view(), name='subscription-confirm'),
    path('<int:pk>/confirm/', ConfirmSubscriptionView.as_view(), name='subscription-confirm-slash'),
    path('<int:pk>/activate', ActivateSubscriptionView.as_view(), name='subscription-activate'),
    path('<int:pk>/activate/', ActivateSubscriptionView.as_view(), name='subscription-activate-slash'),
    path('<int:pk>/close', CloseSubscriptionView.as_view(), name='subscription-close'),
    path('<int:pk>/close/', CloseSubscriptionView.as_view(), name='subscription-close-slash'),
    path('<int:pk>/pause', PauseSubscriptionView.as_view(), name='subscription-pause'),
    path('<int:pk>/pause/', PauseSubscriptionView.as_view(), name='subscription-pause-slash'),
    path('<int:pk>/resume', ResumeSubscriptionView.as_view(), name='subscription-resume'),
    path('<int:pk>/resume/', ResumeSubscriptionView.as_view(), name='subscription-resume-slash'),
    path('<int:pk>/renew', RenewSubscriptionView.as_view(), name='subscription-renew'),
    path('<int:pk>/renew/', RenewSubscriptionView.as_view(), name='subscription-renew-slash'),
]
