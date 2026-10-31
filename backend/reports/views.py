import csv
from datetime import datetime
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsStaffOrAdmin
from reports import services

class ReportsSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        plan_id = request.query_params.get('plan')
        customer_id = request.query_params.get('customer')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        data = services.get_dashboard_summary(
            start_date=start_date,
            end_date=end_date,
            plan_id=int(plan_id) if plan_id else None,
            customer_id=int(customer_id) if customer_id else None
        )
        return Response(data)

class ActiveSubscriptionsReportView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get(self, request):
        plan_id = request.query_params.get('plan')
        customer_id = request.query_params.get('customer')

        data = services.get_active_subscriptions_report(
            plan_id=int(plan_id) if plan_id else None,
            customer_id=int(customer_id) if customer_id else None
        )
        return Response(data)

class RevenueReportView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        plan_id = request.query_params.get('plan')
        customer_id = request.query_params.get('customer')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        data = services.get_revenue_by_month(
            start_date=start_date,
            end_date=end_date,
            plan_id=int(plan_id) if plan_id else None,
            customer_id=int(customer_id) if customer_id else None
        )
        return Response(data)

class OverdueInvoicesReportView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get(self, request):
        plan_id = request.query_params.get('plan')
        customer_id = request.query_params.get('customer')

        data = services.get_overdue_invoices_report(
            plan_id=int(plan_id) if plan_id else None,
            customer_id=int(customer_id) if customer_id else None
        )
        return Response(data)

class ExportReportsCSVView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get(self, request):
        report_type = request.query_params.get('type', 'overdue')
        plan_id = request.query_params.get('plan')
        customer_id = request.query_params.get('customer')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="report_{report_type}.csv"'

        writer = csv.writer(response)

        if report_type == 'overdue':
            writer.writerow(['Invoice Number', 'Customer Email', 'Due Date', 'Days Overdue', 'Total', 'Amount Paid', 'Balance'])
            rows = services.get_overdue_invoices_report(
                plan_id=int(plan_id) if plan_id else None,
                customer_id=int(customer_id) if customer_id else None
            )
            for r in rows:
                writer.writerow([r['number'], r['customer_email'], r['due_date'], r['days_overdue'], r['total'], r['amount_paid'], r['balance']])
        elif report_type == 'revenue':
            writer.writerow(['Month', 'Revenue', 'Payment Count'])
            rows = services.get_revenue_by_month(
                plan_id=int(plan_id) if plan_id else None,
                customer_id=int(customer_id) if customer_id else None
            )
            for r in rows:
                writer.writerow([r['month'], r['revenue'], r['payment_count']])
        else:
            writer.writerow(['Subscription Number', 'Customer Email', 'Plan', 'Billing Period', 'Recurring Total', 'MRR', 'Status'])
            rows = services.get_active_subscriptions_report(
                plan_id=int(plan_id) if plan_id else None,
                customer_id=int(customer_id) if customer_id else None
            )
            for r in rows:
                writer.writerow([r['number'], r['customer_email'], r['plan_name'], r['billing_period'], r['recurring_total'], r['mrr'], r['status']])

        return response
