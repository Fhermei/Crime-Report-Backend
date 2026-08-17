from rest_framework import permissions

class IsPoliceOrAdmin(permissions.BasePermission):
    message = "Only police or admin accounts can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("police", "admin")
        )

class IsAdminRole(permissions.BasePermission):
    message = "Only admin accounts can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")

class IsPoliceRole(permissions.BasePermission):
    message = "Only police accounts can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "police")