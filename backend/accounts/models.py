from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based access control for VulnReport."""

    class Role(models.TextChoices):
        VIEWER = "viewer", "Viewer"
        PENTESTER = "pentester", "Pentester"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text="Role determining the user's permissions in the system.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Database model
    class Meta:
        ordering = ["-date_joined"]

    # ---- convenience properties ----

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    @property
    def is_pentester(self) -> bool:
        return self.role == self.Role.PENTESTER

    @property
    def is_viewer(self) -> bool:
        return self.role == self.Role.VIEWER

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
