from django.urls import path
from plans.views import PlanListCreateView, PlanDetailView

urlpatterns = [
    path('', PlanListCreateView.as_view(), name='plan-list-create'),
    path('<int:pk>', PlanDetailView.as_view(), name='plan-detail'),
    path('<int:pk>/', PlanDetailView.as_view(), name='plan-detail-slash'),
]
