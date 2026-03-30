from django.db import models


class KBEntry(models.Model):
    """A knowledge-base entry describing a vulnerability class or technique."""

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    name = models.CharField(max_length=255)
    description = models.TextField()
    recommendation = models.TextField(blank=True, default="")
    references = models.TextField(
        blank=True,
        default="",
        help_text="OWASP / CWE references.",
    )
    severity_default = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.MEDIUM,
    )
    category = models.CharField(
        max_length=100,
        help_text="e.g. 'injection', 'auth', 'xss', 'csrf', 'ssrf', 'idor', 'misc'.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "KB entry"
        verbose_name_plural = "KB entries"

    def __str__(self) -> str:
        return f"[{self.category}] {self.name}"


class Resource(models.Model):
    """An external resource (lab, cheatsheet, tool, guide) useful for pentesters."""

    title = models.CharField(max_length=255)
    url = models.URLField(max_length=500)
    description = models.TextField(blank=True, default="")
    category = models.CharField(
        max_length=100,
        help_text="e.g. 'lab', 'cheatsheet', 'tool', 'guide'.",
    )

    class Meta:
        ordering = ["category", "title"]
        verbose_name = "Resource"
        verbose_name_plural = "Resources"

    def __str__(self) -> str:
        return self.title
