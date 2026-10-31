from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser))

class IsStaffOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role in ['admin', 'staff'] or request.user.is_staff or request.user.is_superuser))

class IsAdminOrReadOnlyStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
        if request.method in ('GET', 'HEAD', 'OPTIONS') and request.user.role in ['admin', 'staff']:
            return True
        return False
