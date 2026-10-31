from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from core.permissions import IsStaffOrAdmin
from billing.services import run_billing

@api_view(['POST'])
@permission_classes([IsStaffOrAdmin])
def run_billing_view(request):
    """
    POST /api/billing/run/
    Optional body: {"as_of": "2026-10-31"}
    Returns the summary {created, skipped, failed: [{subscription, reason}]}
    Accessible by Admin and Staff.
    """
    as_of = request.data.get('as_of') if request.data else None
    summary = run_billing(as_of=as_of)
    return Response(summary)
