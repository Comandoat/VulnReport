from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsAdmin(BasePermission):
    """Allow access only to users with the 'admin' role."""

    def has_permission(self, request: Request, view) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsPentester(BasePermission):
    """Allow access only to users with the 'pentester' role."""

    def has_permission(self, request: Request, view) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "pentester"
        )


class IsPentesterOrAdmin(BasePermission):
    """Allow access to pentesters and admins."""

    def has_permission(self, request: Request, view) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("pentester", "admin")
        )


class IsViewer(BasePermission):
    """Allow access only to users with the 'viewer' role."""

    def has_permission(self, request: Request, view) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "viewer"
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: allow if the requesting user owns the object
    (via an ``owner`` attribute) or is an admin.
    """

    def has_object_permission(self, request: Request, view, obj) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return obj.owner == request.user or request.user.is_admin
