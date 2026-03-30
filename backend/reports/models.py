from django.conf import settings
from django.db import models


class Report(models.Model):
    """Pentest report containing findings."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_PROGRESS = "in_progress", "In Progress"
        FINALIZED = "finalized", "Finalized"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=255)
    context = models.TextField(blank=True, default="")
    executive_summary = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports",
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.status})"


class Finding(models.Model):
    """Individual vulnerability finding within a report."""

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    SEVERITY_ORDER_MAP = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    proof = models.TextField(blank=True, default="")
    impact = models.TextField(blank=True, default="")
    recommendation = models.TextField(blank=True, default="")
    references = models.TextField(blank=True, default="")
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.MEDIUM,
    )
    cvss_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
    )
    order = models.IntegerField(default=0)
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="findings",
    )
    kb_entry = models.ForeignKey(
        "kb.KBEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="findings",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self) -> str:
        return f"{self.title} [{self.severity}]"

    @property
    def severity_order(self) -> int:
        """Return numeric value for severity sorting (lower = more severe)."""
        return self.SEVERITY_ORDER_MAP.get(self.severity, 2)
