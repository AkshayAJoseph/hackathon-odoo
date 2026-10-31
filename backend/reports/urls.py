from django.urls import path
from reports.views import (
    ReportsSummaryView,
    ActiveSubscriptionsReportView,
    RevenueReportView,
    OverdueInvoicesReportView,
    ExportReportsCSVView,
)

urlpatterns = [
    path('summary/', ReportsSummaryView.as_view(), name='reports-summary'),
    path('active-subscriptions/', ActiveSubscriptionsReportView.as_view(), name='reports-active-subscriptions'),
    path('revenue/', RevenueReportView.as_view(), name='reports-revenue'),
    path('overdue/', OverdueInvoicesReportView.as_view(), name='reports-overdue'),
    path('export.csv', ExportReportsCSVView.as_view(), name='reports-export-csv'),
]
