from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""

    list_display = ("username", "email", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)

    # Add 'role' and 'created_at' to the default fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ("VulnReport", {"fields": ("role", "created_at")}),
    )
    readonly_fields = ("created_at",)

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("VulnReport", {"fields": ("role",)}),
    )
