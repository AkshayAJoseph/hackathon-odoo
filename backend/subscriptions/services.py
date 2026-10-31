from django.db import transaction
from core.services import log_transition
from subscriptions.models import Subscription

def close_subscription(sub: Subscription, user=None) -> Subscription:
    """
    Closes an active subscription.
    Can be triggered by a user (requires plan.closable=True) or by Amrutha's billing engine (user=None).
    """
    from_status = sub.status
    sub.status = 'closed'
    sub.save(update_fields=['status', 'updated_at'])
    log_transition(
        actor=user,
        entity='Subscription',
        entity_id=sub.number,
        from_status=from_status,
        to_status='closed'
    )
    return sub
