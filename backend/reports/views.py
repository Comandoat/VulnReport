import logging

from rest_framework import generics, permissions, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Finding, Report
from .permissions import CanViewReport, IsReportOwnerOrAdmin
from .serializers import (
    FindingCreateSerializer,
    FindingSerializer,
    ReportCreateSerializer,
    ReportDetailSerializer,
    ReportListSerializer,
    ReportUpdateSerializer,
)

logger = logging.getLogger(__name__)


def _log_audit(user, action, object_type, object_id, metadata=""):
    """Safely log to the audit system; no-op if audit app is unavailable."""
    try:
        from audit.utils import log_action

        if isinstance(metadata, str):
            metadata = {"detail": metadata}

        log_action(
            actor=user,
            action=action,
            object_type=object_type,
            object_id=object_id,
            metadata=metadata,
        )
    except Exception:
        logger.exception("Failed to write audit log for action=%s", action)


# ---------------------------------------------------------------------------
# Report views
# ---------------------------------------------------------------------------


class ReportListCreateView(generics.ListCreateAPIView):
    """
    GET  — list reports visible to the current user.
    POST — create a new report (pentester / admin only).
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReportCreateSerializer
        return ReportListSerializer

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)
        if role == "admin":
            return Report.objects.all()
        if role == "pentester":
            return Report.objects.filter(owner=user)
        # viewer — published only
        return Report.objects.filter(status="published")

    def get_queryset_filtered(self):
        """Apply optional status query-param filter."""
        qs = self.get_queryset()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset_filtered())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = self.request.user
        role = getattr(user, "role", None)
        if role not in ("pentester", "admin"):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only pentesters and admins can create reports.")
        report = serializer.save(owner=user)
        _log_audit(user, "create_report", "Report", report.id, f"Created report: {report.title}")


class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    — retrieve report (owner / admin / published).
    PATCH  — update report (owner / admin).
    DELETE — delete report (owner / admin).
    """

    queryset = Report.objects.all()

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return ReportUpdateSerializer
        return ReportDetailSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated(), CanViewReport()]
        return [permissions.IsAuthenticated(), IsReportOwnerOrAdmin()]

    def perform_update(self, serializer):
        report = serializer.save()
        _log_audit(
            self.request.user,
            "update_report",
            "Report",
            report.id,
            f"Updated report: {report.title}",
        )

    def perform_destroy(self, instance):
        report_id = instance.id
        report_title = instance.title
        instance.delete()
        _log_audit(
            self.request.user,
            "delete_report",
            "Report",
            report_id,
            f"Deleted report: {report_title}",
        )


# ---------------------------------------------------------------------------
# Finding views
# ---------------------------------------------------------------------------


class FindingListCreateView(generics.ListCreateAPIView):
    """
    GET  — list findings for a report.
    POST — add a finding to a report.
    """

    def get_report(self):
        report = generics.get_object_or_404(Report, pk=self.kwargs["report_id"])
        return report

    def get_serializer_class(self):
        if self.request.method == "POST":
            return FindingCreateSerializer
        return FindingSerializer

    def get_queryset(self):
        return Finding.objects.filter(report_id=self.kwargs["report_id"])

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated(), CanViewReport()]
        return [permissions.IsAuthenticated(), IsReportOwnerOrAdmin()]

    def check_object_permissions(self, request, obj):
        """We check permissions against the *report*, not the finding."""
        for permission in self.get_permissions():
            if hasattr(permission, "has_object_permission"):
                if not permission.has_object_permission(request, self, obj):
                    self.permission_denied(request)

    def list(self, request, *args, **kwargs):
        report = self.get_report()
        self.check_object_permissions(request, report)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        report = self.get_report()
        self.check_object_permissions(self.request, report)
        finding = serializer.save(report=report)
        _log_audit(
            self.request.user,
            "create_finding",
            "Finding",
            finding.id,
            f"Created finding '{finding.title}' in report {report.id}",
        )


class FindingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE a specific finding.
    """

    serializer_class = FindingSerializer

    def get_report(self):
        return generics.get_object_or_404(Report, pk=self.kwargs["report_id"])

    def get_queryset(self):
        return Finding.objects.filter(report_id=self.kwargs["report_id"])

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated(), CanViewReport()]
        return [permissions.IsAuthenticated(), IsReportOwnerOrAdmin()]

    def check_object_permissions(self, request, obj):
        """Check permissions against the parent report."""
        report = self.get_report()
        for permission in self.get_permissions():
            if hasattr(permission, "has_object_permission"):
                if not permission.has_object_permission(request, self, report):
                    self.permission_denied(request)

    def perform_update(self, serializer):
        finding = serializer.save()
        _log_audit(
            self.request.user,
            "update_finding",
            "Finding",
            finding.id,
            f"Updated finding '{finding.title}'",
        )

    def perform_destroy(self, instance):
        finding_id = instance.id
        finding_title = instance.title
        report_id = instance.report_id
        instance.delete()
        _log_audit(
            self.request.user,
            "delete_finding",
            "Finding",
            finding_id,
            f"Deleted finding '{finding_title}' from report {report_id}",
        )


# ---------------------------------------------------------------------------
# Reorder findings
# ---------------------------------------------------------------------------


class ReorderFindingsView(APIView):
    """
    POST — accept a list of finding IDs in desired order and update the
    ``order`` field accordingly.

    Request body: {"finding_ids": [3, 1, 2]}
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, report_id):
        report = generics.get_object_or_404(Report, pk=report_id)

        # Permission check: owner or admin
        user_role = getattr(request.user, "role", None)
        if report.owner != request.user and user_role != "admin":
            return Response(
                {"detail": "You do not have permission to reorder findings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        finding_ids = request.data.get("finding_ids", [])
        if not isinstance(finding_ids, list):
            return Response(
                {"detail": "finding_ids must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate all IDs are integers
        if not all(isinstance(fid, int) for fid in finding_ids):
            return Response(
                {"detail": "All finding IDs must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate all IDs belong to this report
        report_findings = set(
            Finding.objects.filter(report=report).values_list("id", flat=True)
        )
        provided_ids = set(finding_ids)

        if not provided_ids.issubset(report_findings):
            return Response(
                {"detail": "One or more finding IDs do not belong to this report."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Require exact match: all findings must be provided
        if provided_ids != report_findings:
            return Response(
                {"detail": "All finding IDs for the report must be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Bulk update order
        findings_to_update = []
        for idx, fid in enumerate(finding_ids):
            finding = Finding(pk=fid, order=idx)
            findings_to_update.append(finding)

        if findings_to_update:
            Finding.objects.bulk_update(findings_to_update, ["order"])

        _log_audit(
            request.user,
            "reorder_findings",
            "Report",
            report.id,
            f"Reordered {len(finding_ids)} findings",
        )

        return Response({"detail": "Findings reordered successfully."}, status=status.HTTP_200_OK)
