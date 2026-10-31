from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Allows access only to authenticated users with admin role or superusers.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, 'role', None) == 'admin' or getattr(user, 'is_superuser', False)


class IsStaffOrAdmin(BasePermission):
    """
    Allows access to authenticated users who are staff or admin.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        role = getattr(user, 'role', None)
        return (
            role in ('admin', 'staff') or
            getattr(user, 'is_staff', False) or
            getattr(user, 'is_superuser', False)
        )


class IsCustomerOwner(BasePermission):
    """
    Object-level permission allowing customers to only access their own objects.
    Staff and Admin have access to all objects.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Staff and admin can access any object
        role = getattr(user, 'role', None)
        is_staff = getattr(user, 'is_staff', False) is True
        is_superuser = getattr(user, 'is_superuser', False) is True
        if role in ('admin', 'staff') or is_staff or is_superuser:
            return True

        # Check ownership
        obj_owner = getattr(obj, 'customer', getattr(obj, 'user', getattr(obj, 'actor', None)))
        if obj_owner is not None:
            return obj_owner == user

        # Direct user object
        if obj == user:
            return True

        return False
