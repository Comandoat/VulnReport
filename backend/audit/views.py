from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView

from accounts.permissions import IsAdmin

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(ListAPIView):
    """
    GET /api/audit/logs/
    Admin-only. Lists all audit log entries, newest first.
    Supports filtering by action, object_type, and actor (user id).
    """

    queryset = AuditLog.objects.select_related("actor").all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["action", "object_type", "actor"]
