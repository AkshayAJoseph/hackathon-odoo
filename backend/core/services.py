from django.db.models import QuerySet
from core.models import AuditLog

def log_transition(actor, entity: str, entity_id: str, from_status: str, to_status: str) -> AuditLog:
    """
    Creates an AuditLog entry for any entity state transition.
    Actor can be None when triggered automatically (e.g. billing engine auto_close).
    """
    return AuditLog.objects.create(
        actor=actor,
        entity=str(entity),
        entity_id=str(entity_id),
        from_status=str(from_status),
        to_status=str(to_status)
    )

def scoped_queryset(user, qs: QuerySet, user_field: str = 'customer') -> QuerySet:
    """
    Filters a queryset based on user role:
    - Anonymous / None: empty queryset (qs.none())
    - Admin or Staff: full queryset (qs.all())
    - Customer: filtered to records belonging to that customer.
    """
    if not user or not getattr(user, 'is_authenticated', False):
        return qs.none()

    # Admin and staff have unrestricted visibility
    role = getattr(user, 'role', None)
    if role in ('admin', 'staff') or getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
        return qs.all()

    # Customer scope
    model = qs.model
    field_names = [f.name for f in model._meta.get_fields()]

    if user_field in field_names:
        return qs.filter(**{user_field: user})
    elif 'customer' in field_names:
        return qs.filter(customer=user)
    elif 'user' in field_names:
        return qs.filter(user=user)
    elif 'actor' in field_names:
        return qs.filter(actor=user)

    return qs.none()
