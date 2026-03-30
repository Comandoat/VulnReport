from rest_framework import serializers

from .models import AuditLog


class _ActorInlineSerializer(serializers.Serializer):
    """Minimal read-only representation of the actor."""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)


class AuditLogSerializer(serializers.ModelSerializer):
    actor = _ActorInlineSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "actor",
            "action",
            "object_type",
            "object_id",
            "timestamp",
            "metadata",
        ]
        read_only_fields = fields
