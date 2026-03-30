from .models import AuditLog


def log_action(actor, action, object_type, object_id="", metadata=None):
    """Log an action to the audit trail. Never include sensitive data in metadata."""
    AuditLog.objects.create(
        actor=actor,
        action=action,
        object_type=object_type,
        object_id=str(object_id),
        metadata=metadata or {},
    )
