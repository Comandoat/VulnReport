from rest_framework import serializers

from .models import Finding, Report
from kb.models import KBEntry


VALID_STATUS_TRANSITIONS = {
    "draft": ["in_progress"],
    "in_progress": ["finalized"],
    "finalized": ["published"],
    "published": [],
}


class OwnerSerializer(serializers.Serializer):
    """Lightweight nested representation of a user."""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)


def _validate_cvss_score(value):
    """Validate that a CVSS score is between 0.0 and 10.0."""
    if value is not None and (value < 0.0 or value > 10.0):
        raise serializers.ValidationError(
            "CVSS score must be between 0.0 and 10.0."
        )
    return value


class FindingSerializer(serializers.ModelSerializer):
    """Full representation of a finding."""

    kb_entry = serializers.PrimaryKeyRelatedField(
        queryset=KBEntry.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Finding
        fields = [
            "id",
            "title",
            "description",
            "proof",
            "impact",
            "recommendation",
            "references",
            "severity",
            "cvss_score",
            "order",
            "report",
            "kb_entry",
            "created_at",
            "severity_order",
        ]
        read_only_fields = ["id", "report", "created_at", "severity_order"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lazily resolve the KBEntry queryset to avoid import errors if kb
        # app hasn't been migrated yet.
        try:
            from kb.models import KBEntry

            self.fields["kb_entry"].queryset = KBEntry.objects.all()
        except Exception:
            self.fields["kb_entry"].queryset = Finding.objects.none()

    def validate_cvss_score(self, value):
        return _validate_cvss_score(value)


class FindingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a finding, with optional KBEntry pre-fill."""

    kb_entry = serializers.PrimaryKeyRelatedField(
        queryset=KBEntry.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Finding
        fields = [
            "title",
            "description",
            "proof",
            "impact",
            "recommendation",
            "references",
            "severity",
            "cvss_score",
            "kb_entry",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from kb.models import KBEntry

            self.fields["kb_entry"].queryset = KBEntry.objects.all()
        except Exception:
            self.fields["kb_entry"].queryset = Finding.objects.none()

    def validate_cvss_score(self, value):
        return _validate_cvss_score(value)

    def create(self, validated_data):
        kb_entry = validated_data.get("kb_entry")
        if kb_entry is not None:
            # Pre-fill empty fields from the knowledge-base entry.
            prefill_fields = [
                "title",
                "description",
                "impact",
                "recommendation",
                "references",
                "severity",
            ]
            for field in prefill_fields:
                if not validated_data.get(field) and hasattr(kb_entry, field):
                    kb_value = getattr(kb_entry, field, "")
                    if kb_value:
                        validated_data[field] = kb_value
        return super().create(validated_data)


class ReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for report lists."""

    owner = OwnerSerializer(read_only=True)
    findings_count = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "title",
            "status",
            "created_at",
            "updated_at",
            "owner",
            "findings_count",
        ]

    def get_findings_count(self, obj) -> int:
        return obj.findings.count()


class ReportDetailSerializer(serializers.ModelSerializer):
    """Full representation of a report including nested findings."""

    owner = OwnerSerializer(read_only=True)
    findings = FindingSerializer(many=True, read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "title",
            "context",
            "executive_summary",
            "status",
            "created_at",
            "updated_at",
            "owner",
            "findings",
        ]


class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new report."""

    class Meta:
        model = Report
        fields = ["id", "title", "context", "executive_summary", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def create(self, validated_data):
        validated_data.setdefault("status", "draft")
        return super().create(validated_data)


class ReportUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating an existing report."""

    class Meta:
        model = Report
        fields = ["title", "context", "executive_summary", "status"]
        extra_kwargs = {
            "title": {"required": False},
            "context": {"required": False},
            "executive_summary": {"required": False},
            "status": {"required": False},
        }

    def validate_status(self, value):
        """Validate status transitions. Admins can set any status."""
        instance = self.instance
        if instance is None:
            return value

        request = self.context.get("request")
        user_role = getattr(request.user, "role", None) if request else None

        # Admins bypass transition validation — they can set any status
        if user_role == "admin":
            return value

        current_status = instance.status
        allowed_transitions = VALID_STATUS_TRANSITIONS.get(current_status, [])

        if value != current_status and value not in allowed_transitions:
            raise serializers.ValidationError(
                f"Cannot transition from '{current_status}' to '{value}'. "
                f"Allowed transitions: {allowed_transitions or 'none'}."
            )

        return value

    def validate(self, attrs):
        """Check that only admins can set status to published."""
        new_status = attrs.get("status")
        if new_status == "published":
            request = self.context.get("request")
            if request is None:
                raise serializers.ValidationError(
                    {"status": "Cannot determine user role for publishing."}
                )
            user_role = getattr(request.user, "role", None)
            if user_role != "admin":
                raise serializers.ValidationError(
                    {"status": "Only admins can publish reports."}
                )
        return attrs
