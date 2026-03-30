from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Immutable audit trail for security-relevant actions."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )
    action = models.CharField(
        max_length=100,
        help_text=(
            "Action performed, e.g. 'login', 'logout', 'create_report', "
            "'update_report', 'delete_report', 'create_finding', "
            "'update_finding', 'delete_finding', 'create_kb_entry', "
            "'update_kb_entry', 'delete_kb_entry', 'update_user_role', "
            "'activate_user', 'deactivate_user'."
        ),
    )
    object_type = models.CharField(
        max_length=100,
        help_text="Type of object affected, e.g. 'report', 'finding', 'kb_entry', 'user', 'session'.",
    )
    object_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Primary key of the affected object.",
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extra context (never include sensitive data).",
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit log entry"
        verbose_name_plural = "Audit log entries"

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.actor} - {self.action}"
