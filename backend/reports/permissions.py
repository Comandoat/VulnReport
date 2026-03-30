from rest_framework.permissions import BasePermission


class IsReportOwner(BasePermission):
    """Allow access only to the report owner."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsReportOwnerOrAdmin(BasePermission):
    """Allow access to the report owner or admin users."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or getattr(request.user, "role", None) == "admin"


class CanViewReport(BasePermission):
    """Allow viewing if owner, admin, or report is published."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        if getattr(request.user, "role", None) == "admin":
            return True
        if obj.status == "published":
            return True
        return False
