from datetime import date
from django.db.models import F
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permissions import IsStaffOrAdmin
from billing.models import Invoice
from billing.serializers import InvoiceSerializer
from billing.services import confirm_invoice, cancel_invoice, mark_sent
from payments.services import record_payment
from payments.serializers import PaymentSerializer

class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Invoice.objects.select_related('customer', 'subscription').prefetch_related('lines').order_by('-id')

        # Role-based query isolation
        if user.role == 'customer':
            qs = qs.filter(customer=user)

        # Filters
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        customer_param = self.request.query_params.get('customer')
        if customer_param and user.role in ['admin', 'staff']:
            qs = qs.filter(customer_id=customer_param)

        subscription_param = self.request.query_params.get('subscription')
        if subscription_param:
            qs = qs.filter(subscription_id=subscription_param)

        overdue_param = self.request.query_params.get('overdue')
        if overdue_param and overdue_param.lower() in ['true', '1']:
            today = date.today()
            qs = qs.filter(status='confirmed', due_date__lt=today, total__gt=F('amount_paid'))

        start_date = self.request.query_params.get('start_date')
        if start_date:
            qs = qs.filter(issue_date__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            qs = qs.filter(issue_date__lte=end_date)

        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsStaffOrAdmin])
    def confirm(self, request, pk=None):
        invoice = self.get_object()
        try:
            confirmed = confirm_invoice(invoice, actor=request.user)
            return Response(self.get_serializer(confirmed).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsStaffOrAdmin])
    def cancel(self, request, pk=None):
        invoice = self.get_object()
        try:
            cancelled = cancel_invoice(invoice, actor=request.user)
            return Response(self.get_serializer(cancelled).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsStaffOrAdmin])
    def send(self, request, pk=None):
        invoice = self.get_object()
        sent = mark_sent(invoice, actor=request.user)
        return Response(self.get_serializer(sent).data)

    @action(detail=True, methods=['post'], permission_classes=[IsStaffOrAdmin])
    def payments(self, request, pk=None):
        invoice = self.get_object()
        method = request.data.get('method')
        amount = request.data.get('amount')
        payment_date = request.data.get('payment_date')
        note = request.data.get('note', '')

        if not method or amount is None:
            return Response({'error': 'method and amount are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = record_payment(
                invoice=invoice,
                method=method,
                amount=amount,
                payment_date=payment_date,
                note=note,
                user=request.user
            )
            return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def print(self, request, pk=None):
        invoice = self.get_object()

        lines_html = ""
        for line in invoice.lines.all():
            lines_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{line.description}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: center;">{line.quantity}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">${line.unit_price}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">${line.discount}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">{line.tax_rate}%</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">${line.tax_amount}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600;">${line.line_total}</td>
            </tr>
            """

        status_color = "#10b981" if invoice.status == 'paid' else ("#f59e0b" if invoice.status == 'confirmed' else "#6b7280")
        if invoice.is_overdue():
            status_color = "#ef4444"

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Invoice {invoice.number}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1f2937; margin: 40px; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #3b82f6; padding-bottom: 20px; }}
        .company {{ font-size: 24px; font-weight: bold; color: #1e40af; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; font-weight: bold; text-transform: uppercase; font-size: 12px; background: {status_color}; color: white; }}
        .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #f3f4f6; text-align: left; padding: 12px 10px; border-bottom: 2px solid #e5e7eb; }}
        .summary {{ margin-top: 30px; margin-left: auto; width: 300px; }}
        .summary-row {{ display: flex; justify-content: space-between; padding: 6px 0; }}
        .summary-total {{ font-size: 18px; font-weight: bold; border-top: 2px solid #1f2937; margin-top: 6px; padding-top: 6px; }}
        @media print {{
            body {{ margin: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="company">Brightloop Software</div>
            <div>Subscription Management & Billing</div>
            <div>billing@brightloop.test</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 28px; font-weight: bold;">INVOICE</div>
            <div style="font-size: 16px; color: #4b5563;">{invoice.number}</div>
            <div style="margin-top: 6px;"><span class="badge">{invoice.status}</span></div>
        </div>
    </div>

    <div class="meta-grid">
        <div>
            <strong>Billed To:</strong><br>
            {invoice.customer.name or invoice.customer.email}<br>
            Email: {invoice.customer.email}<br>
            {f"Company: {invoice.customer.company}<br>" if getattr(invoice.customer, 'company', None) else ""}
        </div>
        <div style="text-align: right;">
            <strong>Issue Date:</strong> {invoice.issue_date}<br>
            <strong>Due Date:</strong> {invoice.due_date}<br>
            <strong>Billing Period:</strong> {invoice.period_start} to {invoice.period_end}<br>
            <strong>Subscription:</strong> {invoice.subscription.number}
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Description</th>
                <th style="text-align: center;">Qty</th>
                <th style="text-align: right;">Unit Price</th>
                <th style="text-align: right;">Discount</th>
                <th style="text-align: right;">Tax Rate</th>
                <th style="text-align: right;">Tax</th>
                <th style="text-align: right;">Total</th>
            </tr>
        </thead>
        <tbody>
            {lines_html}
        </tbody>
    </table>

    <div class="summary">
        <div class="summary-row"><span>Subtotal:</span><span>${invoice.subtotal}</span></div>
        <div class="summary-row"><span>Discount:</span><span>-${invoice.discount_total}</span></div>
        <div class="summary-row"><span>Tax:</span><span>${invoice.tax_total}</span></div>
        <div class="summary-row summary-total"><span>Total:</span><span>${invoice.total}</span></div>
        <div class="summary-row"><span>Amount Paid:</span><span>${invoice.amount_paid}</span></div>
        <div class="summary-row" style="color: {'#ef4444' if invoice.balance > 0 else '#10b981'}; font-weight: bold;">
            <span>Outstanding Balance:</span><span>${invoice.balance}</span>
        </div>
    </div>
</body>
</html>"""
        return HttpResponse(html_content, content_type='text/html')
